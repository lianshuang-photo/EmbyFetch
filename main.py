import requests
import json
import os
import time
import configparser

file = 'config.ini'
# 创建配置文件对象
config = configparser.ConfigParser()
# 读取文件
config.read(file, encoding='utf-8')

# 下载路径
download_path = config['download']['download_path']

# emby配置
url = config['emby']['url']
username = config['emby']['username']
password = config['emby']['password']
api_key = config['emby']['api_key']
user_id = config['emby']['user_id']

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'X-Emby-Authorization': 'MediaBrowser Client="Emby Web", Device="Chrome", DeviceId="xyz123", Version="4.7.11.0"'
}

# 获取媒体信息类型
def main(mediaId):
    response = json.loads(requests.get(f"{url}/emby/Users/{user_id}/Items/{mediaId}?api_key={api_key}", headers=headers).text)
    print(f"媒体类型： {response['Type']}")
    if(response['Type'] == 'Movie'):# 电影
        print(f"电影名称： {response['Name']}  年份：{response['ProductionYear']}\nFileName： {response['FileName']}")
        getDownloadInfo(response['Name'],"",mediaId)
    elif(response['Type'] == 'Series'):# 整部剧集
        print(f"剧集名称： {response['Name']}  年份：{response['ProductionYear']}")
        print(f"季数：  共 {response['ChildCount']} 季")
        re = json.loads(requests.get(f"{url}/emby/Shows/{mediaId}/Seasons?api_key={api_key}", headers=headers).text)['Items']
        for item in re:
            print(f"剧集：【{item['SeriesName']}】    季： {item['Name']}   Id： {item['Id']}")
        if(len(re) == 1):
            ok = input("当前剧集共1季，是否确认下载(y/n)：") or "y"
            if(ok == 'y'):
                getEpisodesInfo(mediaId,re[0]['Id'])
            else:
                print("取消下载")
        else:
            inputSeasonNum = input("请输入需要下载的IndexNumber(1,2,3具体下载某一季，输入a下载所有季)：") or "a"
            if(inputSeasonNum.isdigit()):
                print(f"当前下载第 {inputSeasonNum} 季")
                inputSeasonNum = int(inputSeasonNum) - 1
                getEpisodesInfo(mediaId,re[inputSeasonNum]['Id'])
            elif(inputSeasonNum == 'a' or inputSeasonNum == 'A'):
                print("当前下载所有季")
                for x in re:
                    getEpisodesInfo(mediaId,x['Id'])

    elif(response['Type'] == 'Season'):# 剧集中的某一季
        print(f"剧集名称： {response['SeriesName']}  年份：{response['ProductionYear']}")
        print(f"集数：  共 {response['ChildCount']} 集")
        ok = input("是否确认下载(y/n)：") or "y"
        if(ok == 'y'):
            getEpisodesInfo(response['ParentId'],response['Id'])
        else:
            print("取消下载")
    elif(response['Type'] == 'Episode'):# 季中的某一集
        print(f"剧集名称： {response['SeriesName']}  年份：{response['ProductionYear']}")
        print(f"当前下载： {response['SeriesName']} - {response['SeasonName']} - 第 {response['IndexNumber']} 集 - {response['Name']}")
        getDownloadInfo(response['SeriesName'],response['SeasonName'],response['Id'])
    else:
        print("媒体类型错误")
          
# 获取季信息
def getEpisodesInfo(tvId,SeasonId):
    response = json.loads(requests.get(f"{url}/emby/Shows/{tvId}/Episodes?SeasonId={SeasonId}&Limit=1000&ImageTypeLimit=1&UserId={user_id}&api_key={api_key}", headers=headers).text)
    for x in response['Items']:
        SeriesName = x['SeriesName']
        SeasonName = x['SeasonName']
        Name = x['Name']
        IndexNumber = x['IndexNumber']
        Id = x['Id']
        print(f"当前下载： {SeriesName} - {SeasonName} - 第 {IndexNumber} 集 - {Name}")
        getDownloadInfo(SeriesName,SeasonName,Id)

# 获取播放信息
def getDownloadInfo(MediaName,SeasonName,Id):
    response = json.loads(requests.get(f"{url}/emby/Items/{Id}/PlaybackInfo?UserId={user_id}&api_key={api_key}", headers=headers).text)
    media_sources = response['MediaSources']
    
    if len(media_sources) > 1:
        print("\n可用画质:")
        for i, source in enumerate(media_sources):
            size_mb = source.get('Size', 0) / (1024 * 1024)
            container = source.get('Container', 'mkv')
            name = source.get('Name', '')
            
            # 构建完整的文件路径
            full_path = f"{MediaName}/{SeasonName}/{name}.{container}"
            print(f"{i+1}. {full_path} - 大小: {size_mb:.2f}MB")
        
        while True:
            try:
                choice = int(input("\n请选择画质 (输入序号): ")) - 1
                if 0 <= choice < len(media_sources):
                    x = media_sources[choice]
                    break
                else:
                    print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")
    else:
        x = media_sources[0]
    
    Name = x['Name']
    Container = x['Container']
    MediaSourcesId = x['Id']
    playUrl = f"{url}/videos/{Id}/stream.{Container}?api_key={api_key}&MediaSourceId={MediaSourcesId}&Static=true" 
    fileSize = x.get('Size', '')
    if (fileSize != ''):
        fileSize = str(round(fileSize / 1024 / 1024, 2)) + ' MB' #兆字节
        print(f"文件大小：{fileSize}")
    print(f"下载地址： {playUrl}")
    savePath = f"/{MediaName}/{SeasonName}"
    saveName = f"/{Name}.{Container}"
    downloadProgressbar(playUrl, savePath, saveName)

def getPlayerUrl(Id):
    # 首先获取媒体信息
    media_info = json.loads(requests.get(f"{url}/emby/Users/{user_id}/Items/{Id}?api_key={api_key}", headers=headers).text)
    
    if media_info['Type'] == 'Episode':
        MediaName = media_info['SeriesName']
        SeasonName = media_info['SeasonName']
        print(f"剧集名称： {MediaName} - {SeasonName} - 第 {media_info['IndexNumber']} 集 - {media_info['Name']}")
    else:
        MediaName = media_info['Name']
        SeasonName = ""
        print(f"媒体名称： {MediaName}")

    # 获取播放信息
    response = json.loads(requests.get(f"{url}/emby/Items/{Id}/PlaybackInfo?UserId={user_id}&api_key={api_key}", headers=headers).text)
    media_sources = response['MediaSources']
    
    if len(media_sources) > 1:
        print("\n可用画质:")
        for i, source in enumerate(media_sources):
            size_mb = source.get('Size', 0) / (1024 * 1024)
            container = source.get('Container', 'mkv')
            name = source.get('Name', '')
            
            # 构建完整的文件路径
            if SeasonName:
                full_path = f"{MediaName}/{SeasonName}/{name}.{container}"
            else:
                full_path = f"{MediaName}/{name}.{container}"
            print(f"{i+1}. {full_path} - 大小: {size_mb:.2f}MB")
        
        while True:
            try:
                choice = int(input("\n请选择画质 (输入序号): ")) - 1
                if 0 <= choice < len(media_sources):
                    x = media_sources[choice]
                    break
                else:
                    print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")
    else:
        x = media_sources[0]
        size_mb = x.get('Size', 0) / (1024 * 1024)
        print(f"\n仅有一个画质版本 - 大小: {size_mb:.2f}MB")
    
    Name = x['Name']
    Container = x['Container']
    MediaSourcesId = x['Id']
    playUrl = f"{url}/videos/{Id}/stream.{Container}?api_key={api_key}&MediaSourceId={MediaSourcesId}&Static=true"
    
    if SeasonName:
        full_path = f"{MediaName}/{SeasonName}/{Name}.{Container}"
    else:
        full_path = f"{MediaName}/{Name}.{Container}"
    
    print(f"\n文件路径: {full_path}")
    print(f"播放地址: {playUrl}")

def downloadProgressbar(downloadUrl,savePath,saveName):
    savePath = download_path + savePath
    if not os.path.exists(savePath): # 看是否有该文件夹，没有则创建文件夹
        os.makedirs(savePath)
    start = time.time() #下载开始时间
    
    try:
        print(f'正在下载到: {savePath}{saveName}')
        response = requests.get(downloadUrl, stream=True, headers=headers)
        
        if response.status_code != 200:
            print(f'下载失败，状态码: {response.status_code}')
            return
            
        # 获取文件大小
        content_size = response.headers.get('content-length')
        if content_size is None:
            print('无法获取文件大小，开始下载...')
            # 直接下载，不显示进度
            filepath = savePath+saveName
            with open(filepath,'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            end = time.time()
            print('下载完成! 用时: %.2f秒' % (end - start))
            return
            
        content_size = int(content_size)
        chunk_size = 8192 # 每次下载的数据大小
        size = 0 #初始化已下载大小

        print('开始下载，文件大小: {:.2f} MB'.format(content_size / 1024 / 1024))
        filepath = savePath+saveName
        with open(filepath,'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    size += len(chunk)
                    print('\r下载进度: [{}] {:.2f}%'.format(
                        '>'*int(size*50/content_size),
                        float(size/content_size*100)
                    ), end=' ')
        
        end = time.time()
        print('\n下载完成! 用时: %.2f秒' % (end - start))
        
    except Exception as e:
        print(f'下载出错: {str(e)}')
        # 如果文件下载失败，删除部分下载的文件
        if os.path.exists(savePath+saveName):
            try:
                os.remove(savePath+saveName)
                print('已删除未完成的文件')
            except:
                pass

def login():
    global user_id
    global api_key
    if(api_key == ""):
        data = {
            'Username': username,
            'Pw': password,
        }
        response = json.loads(requests.post(
            url + "/emby/Users/authenticatebyname",
            headers=headers,
            json=data
        ).text)
        user_id = response['User']['Id']
        api_key = response['AccessToken']
        config.set('emby','user_id',response['User']['Id'])
        config.set('emby','api_key',response['AccessToken'])
        config.write(open(file,'w'))
     
def search(keyword):
    response = json.loads(requests.get(f"{url}/emby/Users/{user_id}/Items?SortBy=SortName&SortOrder=Ascending&Fields=BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,Status,EndDate&StartIndex=0&EnableImageTypes=Primary,Backdrop,Thumb&ImageTypeLimit=1&Recursive=true&SearchTerm={keyword}&GroupProgramsBySeries=true&Limit=50&api_key={api_key}", headers=headers).text)
    if(len(response['Items']) == 0):
        print("未搜索到相关数据")
        return
    for x in response['Items']:
        print(f"ID： {x['Id']}    剧集名称：{x['Name']}    类型：{x['Type']}    年份：{x.get('ProductionYear', '未知年份')}")
     
    mediaId = input("请输入需要下载媒体资源ID：\n")
    main(mediaId)

if __name__ == '__main__':
    try:
        print("正在连接服务器...")
        response = requests.get(f"{url}/emby/system/info/public", headers=headers)
        print(f"服务器响应状态码: {response.status_code}")
        print(f"服务器响应内容: {response.text}")
        response_json = json.loads(response.text)
        print("emby地址："+url)
        print("媒体库："+response_json['ServerName'])
        login()
        while True:
            print("\n1、直接输入媒体ID下载\n2、关键词搜索下载\n3、根据媒体ID获取播放地址：\n")
            option = input("请选择功能（输入q退出）：\n")
            if option.lower() == 'q':
                print("程序已退出")
                break
            elif(option == '1'):
                mediaid = input("请输入媒体id：\n")
                main(mediaid)
            elif(option == '2'):
                keyword = input("请输入搜索关键词：\n")
                search(keyword)
            elif(option == '3'):
                while True:
                    mediaid = input("\n请输入媒体id（输入q返回主菜单）： \n")
                    if mediaid.lower() == 'q':
                        break
                    getPlayerUrl(mediaid)
    except Exception as e:
        print(f"发生错误: {str(e)}")