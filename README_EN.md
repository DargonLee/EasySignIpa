### EasySignIpa

> A command-line utility for re-signing iOS IPA files.` The IPA file needs to be a cracked package.`

### Preparation

- macOS
- Xcode
- Python 3.8+

### Installation

- local installation.

```python
git clone https://github.com/DargonLee/EasySignIpa
cd EasySignIpa
python setup.py install_command
pip install .
```

- pip installation （coming soon）

```python
pip install -U esign
```

### Examples

- Configure the re-signing certificate identity value and provisioning profile.

```python
esign -c
```
Enter the paths for the certificate and provisioning profile.

`Attention⚠️: The certificate and provisioning profile must be a match.`

- Re-sign and generate the output file after re-signing.

```python
esign -s /Users/xxx/Desktop/xxx.ipa -o /Users/xxx/Desktop/
esign -s /Users/xxx/Desktop/xxx.app -o /Users/xxx/Desktop/
```

- Re-sign and output the resigned file, while automatically installing it on the device.

`Attention⚠️: The certificate and provisioning profile must be a match.`

```python   
esign -s /Users/xxx/Desktop/xxx.ipa -o /Users/xxx/Desktop/ -b
esign -s /Users/xxx/Desktop/xxx.app -o /Users/xxx/Desktop/ -b
```

- Automatically install on the device after re-signing.

`Attention⚠️: The certificate and provisioning profile must be a match.`
```python
esign -s /Users/xxx/Desktop/xxx.ipa -b
esign -s /Users/xxx/Desktop/xxx.app -b
```


- Uninstall the previously installed app with the same package name on the device after re-signing, and then proceed with the installation.

`Attention⚠️: The certificate and provisioning profile must be a match.`
```python
esign -s /Users/xxx/Desktop/xxx.ipa -rb
esign -s /Users/xxx/Desktop/xxx.app -rb
```

- Re-sign the app and inject a dynamic library or framework.

```python
esign -s /Users/xxx/Desktop/xxx.ipa -l /Users/xxx/Desktop/xxx.dylib
esign -s /Users/xxx/Desktop/xxx.ipa -l /Users/xxx/Desktop/xxx.framework
```