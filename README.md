# 这是一个基于OpenAI的微信公众号服务端程序

## 使用步骤：

1. 修改config.py, 填写你自己的openai api_key， 你自己的微信公众号appID、appSecret 和 token (这些信息在微信公众号管理后台的 *基本配置* 页面可以找到)

2. 启动程序， 在微信公众号管理后台的 *基本配置* 页面， 服务器地址填上  http://ip:80/wx  (ip 为启动python程序的服务器公网地址)


## 支持的功能：
1. 收到微信公众号文字信息后， 会调用ChatGPT的接口， 并回复到微信公众号
2. 如果信息是"画 xxx" 或者 "@xxx"格式， 则会调用openai生成图片的接口， 并将生成的图片回复到微信公众号
3. 如果信息是一张图片， 则会调用openai variation接口， 并将修改后的图片回复到微信公众号
4. 如果信息是语音输入，  则会使用微信的语音识别结果（**需要微信公众号开启语音识别功能**）， 调用ChatGPT接口， 并回复到微信公众号 
5. 如果信息是文件， 则简单的返回文件信息
6. 如果信息是位置，共享， 则简单的返回位置信息

7. 可以直接运行 openai_function.py 来进行测试。
8. openai_test.py 为不使用openai官方库， 直接使用requests模块来进行api调用的测试代码。 功能与openai_function.py基本一致


## 特点：

1. 由于微信对于给服务端的消息，有超时限制
  每5S会重发一次， 最多发3次。 如果一直没有相应，则会在微信公众号显示 服务器错误。
  所以，会对收到的信息作缓存， 如果openai接口不能在14s内返回， 则会返回Exception:Timeout的信息
  如果在超时之前， ChatGPT的回复尚未完整， 则会中断。

2. 用户可以使用"继续", 来继续获取不太完整的答案

3. 如果需要处理图片， 需要系统安装ffmpeg 

## *微信公众号 '阿卡哇卡' 即使用该源码*
