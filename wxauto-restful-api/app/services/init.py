from app.utils.wx_package_manager import wx_manager, get_wx_class, get_wx_function
from pythoncom import CoInitialize
import sys


# 动态导入wx包
WeChat = get_wx_class("WeChat")
Chat = get_wx_class("Chat")
HumanMessage = wx_manager.package.msgs.base.HumanMessage
try:
    get_wx_clients = get_wx_function("get_wx_clients")
except:
    def get_wx_clients():
        return [WeChat()]

# 初始化COM
CoInitialize()

# 导入 wxautox4 额外模块
try:
    WxResponse = wx_manager.package.param.WxResponse
except Exception as e:
    print(f"警告：无法导入WxResponse: {e}")
    WxResponse = None

# 获取微信客户端（全局缓存字典）
WxClient = {}

# 延迟初始化标志
_wechat_initialized = False
_initialization_attempted = False  # 标记是否已尝试过初始化


def safe_initialize_wechat() -> bool:
    """安全地初始化微信客户端

    Returns:
        bool: 是否成功初始化
    """
    global _wechat_initialized, WxClient, _initialization_attempted

    # 如果已经初始化过，直接返回
    if _wechat_initialized:
        return len(WxClient) > 0

    # 标记已尝试初始化
    _initialization_attempted = True

    try:
        # 尝试获取微信客户端
        print("🔍 正在尝试获取微信客户端实例...")
        clients = get_wx_clients()
        if clients:
            for client in clients:
                WxClient[client.nickname] = client
                # 尝试停止监听，如果失败也不影响缓存
                try:
                    client.StopListening()
                except Exception:
                    pass  # 忽略 StopListening 错误
            print(f"✅ 成功初始化 {len(WxClient)} 个微信客户端实例")
            _wechat_initialized = True
            return True
        else:
            print("⚠️  未找到微信客户端")
            _wechat_initialized = True
            return False

    except SystemExit:
        print("❌ wxautox4 未激活，无法创建微信实例")
        print("💡 请先运行以下命令激活：")
        print("   wxautox4 -a your-activation-code")
        _wechat_initialized = True
        return False

    except Exception as e:
        print(f"⚠️  获取微信客户端时出错: {e}")
        print("💡 服务已启动，但微信功能暂时不可用")
        _wechat_initialized = True
        return False


def initialize_wechat_on_startup() -> dict:
    """在服务启动时初始化微信客户端

    Returns:
        dict: 初始化结果 {
            'success': bool,
            'message': str,
            'clients_count': int,
            'clients': list
        }
    """
    global _wechat_initialized, WxClient, _initialization_attempted

    print("\n" + "="*60)
    print("🚀 启动时初始化微信实例")
    print("="*60)

    result = {
        'success': False,
        'message': '',
        'clients_count': 0,
        'clients': []
    }

    try:
        # 尝试获取微信客户端
        print("🔍 正在检测微信客户端...")
        clients = get_wx_clients()

        if clients:
            for client in clients:
                WxClient[client.nickname] = client
                result['clients'].append({
                    'nickname': client.nickname,
                    'logged_in': True
                })
                # 尝试停止监听，如果失败也不影响缓存
                try:
                    client.StopListening()
                except Exception:
                    pass

            result['success'] = True
            result['clients_count'] = len(WxClient)
            result['message'] = f'成功初始化 {len(WxClient)} 个微信客户端实例'

            print(f"✅ {result['message']}")
            for nickname in WxClient.keys():
                print(f"   - {nickname}")

            _wechat_initialized = True
            _initialization_attempted = True
        else:
            result['success'] = False
            result['message'] = '未检测到微信客户端，请确保微信已登录'
            print("⚠️  未检测到微信客户端")
            print("💡 请确保微信已登录，然后调用获取实例接口")

            _wechat_initialized = True
            _initialization_attempted = True

    except SystemExit:
        result['success'] = False
        result['message'] = 'wxautox4 未激活，请先激活后使用'
        print("❌ wxautox4 未激活")
        print("💡 激活方法：")
        print("   wxautox4 -a your-activation-code")
        print("   或在网页中调用 /api/v1/wechat/initialize 接口")

        _wechat_initialized = True
        _initialization_attempted = True

    except Exception as e:
        result['success'] = False
        result['message'] = f'初始化失败: {str(e)}'
        print(f"❌ 初始化失败: {e}")
        print("💡 服务已启动，但微信功能暂时不可用")
        print("💡 可以稍后调用 /api/v1/wechat/initialize 接口重新初始化")

        _wechat_initialized = True
        _initialization_attempted = True

    print("="*60 + "\n")
    return result


def get_initialization_status() -> dict:
    """获取初始化状态

    Returns:
        dict: 初始化状态信息
    """
    return {
        'initialized': _wechat_initialized,
        'attempted': _initialization_attempted,
        'clients_count': len(WxClient),
        'clients': list(WxClient.keys()) if WxClient else []
    }


# 注意：不在模块加载时自动初始化
# 而是延迟到第一次使用时再初始化
print("💡 wxautox4 服务已准备就绪")
print("💡 微信实例将在启动时自动初始化")