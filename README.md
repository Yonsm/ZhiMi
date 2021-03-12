# [https://github.com/Yonsm/ZhiMi](https://github.com/Yonsm/ZhiMi)

XiaoMi Cloud Service for HomeAssistant

## 1. 安装准备

把 `zhimi` 放入 `custom_components`；也支持在 [HACS](https://hacs.xyz/) 中添加自定义库的方式安装。

_依赖 [MiService](https://github.com/Yonsm/MiService)，运行时自动检查安装。_

## 2. 配置方法

参见 [我的 Home Assistant 配置](https://github.com/Yonsm/.homeassistant) 中 [configuration.yaml](https://github.com/Yonsm/.homeassistant/blob/main/configuration.yaml)

```yaml
zhimi:
  username: !secret zhimi_username
  password: !secret zhimi_password
```

- `必选` `username` 小米账号
- `必选` `password` 小米密码

登录后会在 `.storage` 下记录 `zhimi` 的 token 文件，删除后会自动重新登录。

## 3. 使用方式

在其它插件中使用 `get_miio_service()`，如 [ZhiMsg](https://github.com/Yonsm/ZhiMsg)。

后续如果有必要可以暴露其它服务。

## 4. 参考

- [ZhiMsg](https://github.com/Yonsm/ZhiMsg)
- [Yonsm.NET](https://yonsm.github.io)
- [Yonsm's .homeassistant](https://github.com/Yonsm/.homeassistant)
