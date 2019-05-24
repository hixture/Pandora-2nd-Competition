from flask import Flask, send_file, render_template
import json
from io import BytesIO
from lxml import etree


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        """
        只有 Hello World 的首页
        :return:
        """
        return "Hello, world!"

    # TODO: 捕获 404 错误，返回 404.html
    @app.errorhandler(404)
    def page_not_found(error):
        """
        以此项目中的404.html作为此Web Server工作时的404错误页
        """
        return render_template("404.html"),404
        pass

    # TODO: 完成接受 HTTP_URL 的 picture_reshape
    # TODO: 完成接受相对路径的 picture_reshape
    @app.route('/pic', methods=['GET'])
    def picture_reshape():
        """
        **请使用 PIL 进行本函数的编写**
        获取请求的 query_string 中携带的 b64_url 值
        从 b64_url 下载一张图片的 base64 编码，reshape 转为 100*100，并开启抗锯齿（ANTIALIAS）
        对 reshape 后的图片分别使用 base64 与 md5 进行编码，以 JSON 格式返回，参数与返回格式如下

        :param: b64_url:
            本题的 b64_url 以 arguments 的形式给出，可能会出现两种输入
            1. 一个 HTTP URL，指向一张 PNG 图片的 base64 编码结果
            2. 一个 TXT 文本文件的文件名，该 TXT 文本文件包含一张 PNG 图片的 base64 编码结果
                此 TXT 需要通过 SSH 从服务器中获取，并下载到`pandora`文件夹下，具体请参考挑战说明
p
        :return: JSON
        {
            "md5": <图片reshape后的md5编码: str>,
            "base64_picture": <图片reshape后的base64编码: str>
        }
        """

        from PIL import Image
        import base64
        import hashlib
        import requests
        from flask import request
        qs = str(request.args.get('b64_url'))
        if qs[0:4] == 'http':
            b64 = requests.get(qs).text
        else:
            with open('./pandora/'+qs, "r") as f:
                b64 = f.read()
        image = base64.b64decode(b64)
        # filename = 'temp.png'
        # with open(filename, 'wb') as f:
        #     f.write(image)
        img = Image.open(BytesIO(image))
        img = img.resize((100, 100), Image.ANTIALIAS)
        result = BytesIO()
        img.save(result, format='png')
        # with open('temp1.png', "rb") as f:
        f =result.getvalue()
        base64_data = base64.b64encode(f)
        md5_data = hashlib.md5(f).hexdigest()
        res = {"md5": md5_data, "base64_picture": base64_data}
        md5_data = str(md5_data)
        base64_data = str(base64_data)
        # base64_data = base64_data[2:len(base64_data) - 1]
        dic = {}
        dic["md5"] = md5_data
        dic["base64_picture"] = str(base64_data)
        js = json.dumps(dic)
        return js

    # TODO: 爬取 996.icu Repo，获取企业名单
    @app.route('/996')
    def company_996():
        """
        从 github.com/996icu/996.ICU 项目中获取所有的已确认是996的公司名单，并

        :return: 以 JSON List 的格式返回，格式如下
        [{
            "city": <city_name 城市名称>,
            "company": <company_name 公司名称>,
            "exposure_time": <exposure_time 曝光时间>,
            "description": <description 描述>
        }, ...]
        """
        import requests
        import re
        from flask import jsonify
        from flask import Response
        import urllib.request
        import json
        import urllib.request

        url = "http://github.com/996icu/996.ICU"
        black = "/tree/master/blacklist"
        url_black = url + black
        html = requests.get(url_black)
        txt = html.text
        str = ''
        for i in txt:
            str += i
        pattern = re.compile(r'<td align="center">.*</td>')
        result0 = pattern.findall(str)
        result0 = result0[35::]
        # for i in result0:
        #     print(i)
        # print(len(result0))
        res_lst = []  # 结果
        pattern_city = re.compile(r'<td align="center">.*</td>')

        def get_info_0(str):
            pattern = re.compile(r'<td align="center">(.*)</td>')
            r = pattern.findall(str)
            if r == []:
                return None
            return r[0]

        def get_info_1(str):
            pattern = re.compile(r'<.*><.*>(.*)</a></td>')
            r = pattern.findall(str)
            if r == []:
                pattern = re.compile(r'<.*>(.*)</td>')
                r = pattern.findall(str)
            return r[0]

        for i in range(int(len(result0)/5)):
            dic = {}
            for l in range(5):
                # print(l)
                if (l + 1) % 5 == 1:
                    dic["city"] = get_info_0(result0[i * 5 + l])
                if (l + 1) % 5 == 2:
                    dic["company"] = get_info_1(result0[i * 5 + l])
                if (l + 1) % 5 == 3:
                    dic["exposure_time"] = get_info_0(result0[i * 5 + l])
                if (l + 1) % 5 == 4:
                    dic["description"] = get_info_0(result0[i * 5 + l])
            res_lst.append(dic)
        return Response(json.dumps(res_lst),  mimetype='application/json')
        
        pass

    return app
