import subprocess, re

try:
    output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], encoding='gbk')
    profiles = re.findall(r'(?:所有用户配置文件|All User Profile)\s*:\s*(.*)', output)
    for name in profiles:
        try:
            out = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', name, 'key=clear'], encoding='gbk')
            pwd = re.search(r'(?:关键内容|Key Content)\s*:\s*(.*)', out)
            print(f"{name} : {pwd.group(1).strip() if pwd else '无密码'}")
        except:
            print(f"{name} : 获取失败")
except:
    print("请以管理员身份运行本脚本")

input("\n按回车键退出...")