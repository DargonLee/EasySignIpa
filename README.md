### EasySignIpa

![image-20240109170523351](README.assets/image-20240109170523351.png)

### Quick

- macOS
- Xcode
- Python 3.8+

### Install

```python
git clone https://github.com/DargonLee/EasySignIpa
cd EasySignIpa
python setup.py install_command
pip install .
```

### Usage

##### Update resign mobileprovision file

```py
esign update -m debug /Users/xxx/Desktop/xxxx.mobileprovision
esign update -m release /Users/xxx/Desktop/xxxx.mobileprovision
```

##### Update identity value

```py
esign update -m debug 40900B2051FAAB6FED2BCB35C6A42A7C7CE821C1
esign update -m release 40900B2051FAAB6FED2BCB35C6A42A7C7CE821C2
```


##### Output

```python
# ipa 文件输出
esign sign -f /Users/xxx/Desktop/xxx.ipa -o /Users/xxx/Desktop/1.ipa
# app 文件输出
esign sign -f /Users/xxx/Desktop/xxx.app -o /Users/xxx/Desktop/
```

##### Install app to your device

```python
# ipa 文件输出 并安装
esign sign -f /Users/xxx/Desktop/xxx.ipa -o /Users/xxx/Desktop/ -b
# app 文件输出 并安装
esign sign -f /Users/xxx/Desktop/xxx.app -o /Users/xxx/Desktop/ -b
```

##### Reinstall

```python
# ipa 文件重新安装
esign sign -f /Users/xxx/Desktop/xxx.ipa -rb
# app 文件重新安装
esign sign -f /Users/xxx/Desktop/xxx.app -rb
```

##### Injector dylib

```python
# 动态库
esign sign -f /Users/xxx/Desktop/xxx.ipa -l /Users/xxx/Desktop/xxx.dylib -l /Users/xxx/Desktop/yyy.framework
```

### Pycharm Debug

![image-20240524131506385](README.assets/image-20240524131506385.png)
