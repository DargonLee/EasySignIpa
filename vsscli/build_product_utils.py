#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess


def format_jsondata_list(old_path, target_podname):
    json_data_list = get_pre_path_jsondata_list(old_path)
    # print(json_data_list)
    # 先删除原来的依赖
    # remove_pod_dependency(target_podname, 's.dependency')
    remove_pod_dependency(target_podname, "pod")
    for json_obj in json_data_list:
        print(json_obj["link_target"])
        for target_item in json_obj["link_target"]:
            target_pod_name = target_item["target_name"]
            if target_pod_name == target_podname:
                name = target_item["name"]
                version = target_item["version"]
                insert_pod(name, version)
                # insert_pod_to_podspec(target_podname, name)


def get_pre_path_jsondata_list(old_path):
    target_pre_list = chdir_pre_path(old_path)
    json_data_list = []
    for dir_path in target_pre_list:
        if os.path.exists(dir_path):
            json_data = read_package_json(dir_path)
            # print('PackageConfig.json 文件存在', json_data)
            json_data_list.append(json_data)
    return json_data_list


def chdir_pre_path(current_path):
    pre_old_path_list = current_path.split("/")
    pre_old_path_list.pop(len(pre_old_path_list) - 1)
    pre_old_path = "/".join(pre_old_path_list)
    result_list = []
    for root, dirs, files in os.walk(pre_old_path):
        for dir in dirs:
            temp_str = pre_old_path + "/" + dir + "/PackageConfig.json"
            result_list.append(temp_str)

    pre_old_path_list = []
    pre_old_path = ""
    # print(result_list)
    return result_list


def read_package_json(json_file_path):
    with open(json_file_path, "r", encoding="utf8") as fp:
        json_data = json.load(fp)
    fp.close()
    return json_data


def insert_pod(podname, podversion=None):
    """
    插入 pod 'xxx' 组件库 到Podfile文件中
    """
    with open("Podfile", "r") as podfile:
        podfile_list = podfile.readlines()
    podfile.close()
    # 筛选已存在的podname索引值
    podname_index = []
    for index, line in enumerate(podfile_list):
        if line.lstrip().startswith("#"):
            continue
        if line == "\n" or line == " \n":  # 判断是否是空行或注释行
            podfile_list.remove(line)
            continue
        if podname in line:
            podname_index.append(line)

    print(podfile_list)
    for line_index in podname_index:
        podfile_list.remove(line_index)
    print(podfile_list)
    if podversion is not None:
        new_line = "    pod '{}', '{}'\n".format(podname, podversion)
    else:
        new_line = "    pod '{}'\n".format(podname)
    print("更新", new_line)
    podfile_list.insert((len(podfile_list) - 1), new_line)

    new_podfile_str = "".join(podfile_list)
    with open("Podfile", "w+") as new_podfile:
        new_podfile.write(new_podfile_str)
    new_podfile.close()
    del podfile_list


def insert_pod_to_podspec(podname, pod_dependency):
    """
    插入 s.dependency 'xxx' 到yyy.podspec文件中
    """
    pod_file_name = podname + ".podspec"
    with open(pod_file_name, "r") as podfile:
        podfile_list = podfile.readlines()
    podfile.close()
    for index, line in enumerate(podfile_list):
        if podname in line:
            print("{} already exites".format(podname))
    podfile_list.insert(
        (len(podfile_list) - 1), "  s.dependency '{}'\n \n".format(pod_dependency)
    )
    # print(podfile_list)

    new_podfile_str = "".join(podfile_list)
    with open(pod_file_name, "w+") as new_podfile:
        new_podfile.write(new_podfile_str)
    new_podfile.close()
    del podfile_list


def remove_pod_dependency(podname, remove_name):
    pod_file_name = podname + ".podspec"
    with open(pod_file_name, "r") as podfile:
        podfile_list = podfile.readlines()
    podfile.close()
    for index, line in enumerate(podfile_list):
        if remove_name in line:
            podfile_list.pop(index)
            print("{} already remove".format(podname))
    # print(podfile_list)

    new_podfile_str = "".join(podfile_list)
    with open(pod_file_name, "w+") as new_podfile:
        new_podfile.write(new_podfile_str)
    new_podfile.close()
    del podfile_list


def update_pod_version(specname, remove_name):
    with open(specname, "r") as specfile:
        podfile_list = specfile.readlines()
    specfile.close()

    # print(podfile_list)
    for index, line in enumerate(podfile_list):
        if "s.version " in line:
            print(line, index)
            version_string = subprocess.getoutput(
                "grep -E 's.version.*=' {}".format(line)
            )
            print(version_string)

    new_podfile_str = "".join(podfile_list)
    with open(specname, "w+") as new_podfile:
        new_podfile.write(new_podfile_str)
    new_podfile.close()
    del podfile_list


if __name__ == "__main__":
    print("")
    # insert_pod("MBProgressHUD", '1.1.0')
    update_pod_version("./Behavior.podspec", "1.1.0")
