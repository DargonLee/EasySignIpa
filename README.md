# **[中文] | [English](./README_EN.md)**

### EasySignIpa
> 重签名 iOS 的 IPA 文件的命令行工具
`IPA文件需要是咂壳后的包`

### 准备

- macOS
- Xcode
- Python 3.8+

### 安装

- 本地安装

```python
git clone https://github.com/DargonLee/EasySignIpa
cd EasySignIpa
python setup.py install_command
pip install .
```

- pip 安装

```python
pip install -U esign
```

### 示范用例

- 配置重签证书和描述文件

```python
esign -c
```
输入证书identity值和描述文件的路径

`注意⚠️：证书和描述文件是要匹配的`

- 重签名并输出重签后的文件

```python
esign -s /Users/xxx/Desktop/xxx.ipa -o /Users/xxx/Desktop/
esign -s /Users/xxx/Desktop/xxx.app -o /Users/xxx/Desktop/
```

- 重签名并输出重签后的文件，同时自动安装到手机

`注意⚠️：手机要和电脑通过 USB 连接正常`

```python   
esign -s /Users/xxx/Desktop/xxx.ipa -o /Users/xxx/Desktop/ -b
esign -s /Users/xxx/Desktop/xxx.app -o /Users/xxx/Desktop/ -b
```

- 重签名后自动安装到手机

`注意⚠️：手机要和电脑通过 USB 连接正常`
```python
esign -s /Users/xxx/Desktop/xxx.ipa -b
esign -s /Users/xxx/Desktop/xxx.app -b
```


- 重签名后先卸载手机上已经安装同一包名的 App 然后再安装

`注意⚠️：手机要和电脑通过 USB 连接正常`
```python
esign -s /Users/xxx/Desktop/xxx.ipa -rb
esign -s /Users/xxx/Desktop/xxx.app -rb
```

- 重签名 App 并注入动态库

```python
esign -s /Users/xxx/Desktop/xxx.ipa -l /Users/xxx/Desktop/xxx.dylib
esign -s /Users/xxx/Desktop/xxx.ipa -l /Users/xxx/Desktop/xxx.framework
```