#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw WeChat Channel 配置管理工具"""

import os
import sys
import yaml
from pathlib import Path

CONFIG_FILE = Path.home() / ".openclaw" / "extensions" / "wxauto-channel" / "config.yaml"


def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        print(f"错误: 配置文件不存在: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def view_config():
    """查看当前配置"""
    config = load_config()

    print("\n" + "="*50)
    print("  当前监听配置")
    print("="*50)

    print("\n【私聊】")
    private_chats = config.get('private_chats', [])
    if private_chats:
        for i, chat in enumerate(private_chats, 1):
            status = "[ON]" if chat.get('enabled', True) else "[OFF]"
            print(f"  {i}. {status} {chat['name']}")
    else:
        print("  (无)")

    print("\n【群聊】")
    group_chats = config.get('group_chats', [])
    if group_chats:
        for i, chat in enumerate(group_chats, 1):
            status = "[ON]" if chat.get('enabled', True) else "[OFF]"
            mode = chat.get('reply_mode', 'at_me_only')
            mode_text = "仅@我" if mode == 'at_me_only' else "全部"
            print(f"  {i}. {status} {chat['name']} (模式: {mode_text})")
    else:
        print("  (无)")

    print()


def add_private_chat():
    """添加私聊监听"""
    config = load_config()

    print("\n" + "="*50)
    print("  添加私聊监听")
    print("="*50)

    name = input("\n请输入联系人昵称: ").strip()
    if not name:
        print("错误: 昵称不能为空")
        return

    # 检查是否已存在
    private_chats = config.setdefault('private_chats', [])
    if any(c['name'] == name for c in private_chats):
        print(f"错误: 联系人 '{name}' 已存在")
        return

    # 添加新配置
    private_chats.append({
        'name': name,
        'enabled': True
    })

    save_config(config)
    print(f"\n[OK] 成功添加私聊监听: {name}")


def add_group_chat():
    """添加群聊监听"""
    config = load_config()

    print("\n" + "="*50)
    print("  添加群聊监听")
    print("="*50)

    name = input("\n请输入群聊名称: ").strip()
    if not name:
        print("错误: 群聊名称不能为空")
        return

    # 检查是否已存在
    group_chats = config.setdefault('group_chats', [])
    if any(c['name'] == name for c in group_chats):
        print(f"错误: 群聊 '{name}' 已存在")
        return

    # 选择回复模式
    print("\n回复模式:")
    print("  1. 只响应 @我 的消息 (at_me_only)")
    print("  2. 响应所有消息 (all)")

    mode_choice = input("\n请选择 (1-2, 默认1): ").strip()
    reply_mode = 'all' if mode_choice == '2' else 'at_me_only'

    # 添加新配置
    group_chats.append({
        'name': name,
        'enabled': True,
        'reply_mode': reply_mode,
        'sender_whitelist': [],
        'sender_blacklist': []
    })

    save_config(config)
    mode_text = "仅@我" if reply_mode == 'at_me_only' else "全部"
    print(f"\n[OK] 成功添加群聊监听: {name} (模式: {mode_text})")


def delete_listener():
    """删除监听对象"""
    config = load_config()

    print("\n" + "="*50)
    print("  删除监听对象")
    print("="*50)

    # 显示所有监听对象
    all_listeners = []

    print("\n【私聊】")
    for chat in config.get('private_chats', []):
        all_listeners.append(('private', chat['name']))
        print(f"  {len(all_listeners)}. {chat['name']}")

    print("\n【群聊】")
    for chat in config.get('group_chats', []):
        all_listeners.append(('group', chat['name']))
        print(f"  {len(all_listeners)}. {chat['name']}")

    if not all_listeners:
        print("\n没有配置任何监听对象")
        return

    # 选择要删除的对象
    choice = input(f"\n请输入要删除的编号 (1-{len(all_listeners)}): ").strip()

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(all_listeners):
            print("错误: 无效的编号")
            return

        listener_type, name = all_listeners[idx]

        # 删除对象
        if listener_type == 'private':
            config['private_chats'] = [c for c in config.get('private_chats', []) if c['name'] != name]
        else:
            config['group_chats'] = [c for c in config.get('group_chats', []) if c['name'] != name]

        save_config(config)
        print(f"\n[OK] 成功删除: {name}")

    except ValueError:
        print("错误: 请输入有效的数字")


def toggle_listener():
    """启用/禁用监听对象"""
    config = load_config()

    print("\n" + "="*50)
    print("  启用/禁用监听对象")
    print("="*50)

    # 显示所有监听对象
    all_listeners = []

    print("\n【私聊】")
    for chat in config.get('private_chats', []):
        status = "[ON]" if chat.get('enabled', True) else "[OFF]"
        all_listeners.append(('private', chat))
        print(f"  {len(all_listeners)}. {status} {chat['name']}")

    print("\n【群聊】")
    for chat in config.get('group_chats', []):
        status = "[ON]" if chat.get('enabled', True) else "[OFF]"
        all_listeners.append(('group', chat))
        print(f"  {len(all_listeners)}. {status} {chat['name']}")

    if not all_listeners:
        print("\n没有配置任何监听对象")
        return

    # 选择要切换的对象
    choice = input(f"\n请输入要切换的编号 (1-{len(all_listeners)}): ").strip()

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(all_listeners):
            print("错误: 无效的编号")
            return

        listener_type, chat = all_listeners[idx]

        # 切换状态
        chat['enabled'] = not chat.get('enabled', True)

        save_config(config)
        status_text = "启用" if chat['enabled'] else "禁用"
        print(f"\n[OK] 已{status_text}: {chat['name']}")

    except ValueError:
        print("错误: 请输入有效的数字")


def main_menu():
    """主菜单"""
    while True:
        print("\n" + "="*50)
        print("  OpenClaw WeChat Channel - 配置管理")
        print("="*50)
        print("\n1. 查看当前配置")
        print("2. 添加私聊监听")
        print("3. 添加群聊监听")
        print("4. 删除监听对象")
        print("5. 启用/禁用监听对象")
        print("6. 编辑配置文件")
        print("0. 退出")

        choice = input("\n请选择操作 (0-6): ").strip()

        if choice == '1':
            view_config()
        elif choice == '2':
            add_private_chat()
        elif choice == '3':
            add_group_chat()
        elif choice == '4':
            delete_listener()
        elif choice == '5':
            toggle_listener()
        elif choice == '6':
            os.system(f'notepad "{CONFIG_FILE}"')
        elif choice == '0':
            print("\n再见！")
            break
        else:
            print("\n错误: 无效的选择")

        input("\n按回车键继续...")


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)
