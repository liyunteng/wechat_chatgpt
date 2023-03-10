这是一个基于ChatGPT 的微信公众号，服务端程序

1. 本程序会监听 http://ip:80/wx，  将这个地址注册到微信公众号

2. 修改config.py, 填写你自己的openai api_key， 和你自己的微信公众号 appID 和 appSecret token

3. 启动程序， 并在微信公众号页面， 注册 http://ip:80/wx 




支持的功能：
1. 收到微信公众号信息后， 会调用ChatGPT的接口， 并回复到微信公众号
2. 如果信息是"画 xxx" 或者 "@xxx"格式， 则会调用openai生成图片的接口， 并将生成的图片回复到微信公众号
3. 如果信息是一张图片， 则会调用openai ariation接口， 并将修改后的图片回复到微信公众号
4. 如果信息是语音输入，  则会使用微信的语音识别结果（*需要微信公众号开启语音识别功能*）， 调用ChatGPT接口， 并回复到微信公众号 
5. 如果信息是文件， 则简单的返回文件信息
6. 如果信息是位置，共享， 则简单的返回位置信息



特点：

1. 由于微信对于给服务端的消息，有超时限制
  每5S会重发一次， 最多发3次。 如果一直没有相应，则会在微信公众号显示 服务器错误。
  所以，会对受到的信息作缓存， 如果openai接口不能在14s内返回， 则会返回Exception:Timeout的信息
  如果在超时之前， ChatGPT的回复尚未完整， 则会中断。

2. 用户可以使用"继续", 来继续获取不太完整的答案

