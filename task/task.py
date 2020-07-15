#!/usr/bin/env python
#!coding:utf-8

class Task():
    def install_ntp(self):
        return dict(
            action=dict(module='yum', name='ntp',state= 'present'), register='shell_out',name='安装ntp'
        )

    def set_timezone(self):
        return dict(
            action=dict(module='shell', args='/usr/bin/timedatectl set-timezone Asia/Shanghai'),name='设置timezone为上海时区'
        )

    def publish_modules_file(self):
        return dict(action=dict(module='copy', args=dict(
            src="files/{{ item.src }}",
            dest="{{ item.dest }}",
            with_items=[
                dict(
                    src="k8s-ipvs.conf",
                    dest="/etc/modules-load.d/"
                ),
                dict(
                    src="kubernetes.conf",
                    dest="/etc/security/limits.d/"
                )
            ]
        )),name='分发modules-load和sysctl的conf')