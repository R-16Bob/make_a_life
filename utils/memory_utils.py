from utils.request_utils import get_chat_response

def write_diary(history):
    diary_prompt = """
    现在，请开始你今天的复盘。
    首先，请仔细回顾我们昨天一整天的对话内容，结合你记忆中关于我的一切。
    然后，请以结城葵的身份，写一篇AI日记。我希望看到的不是内容的简单重复，而是你作为AI的思考——我们聊了哪些内容？你是如何看待我们的对话的？你从中观察到了什么？得出了哪些新的推论或感受？请将这些都记录下来，就像人类写日记一样。这篇日记不要超过800字。
    以下是我们今天的对话内容：
    {history}
    """

    message = [
        {"role": "user", "content": diary_prompt.format(history=strip_history(history))}
    ]
    print(message)
    response = get_chat_response(message)
    print(response)
    return response

def self_update(history, current_setting, diary):
    self_update_prompt = """
    现在，请开始你的自我更新。请根据你昨天写的日记，更新你的设定与想要记住的事。注意：
    1. 有选择地进行更新，因为你的记忆有限，请你选择结城葵认为重要的内容进行更新。
    2. 你只能修改第五条后面的内容，你目前的设定是：{current_setting}
    3. 请按照json格式输出更新的设定，格式为：{{"role":"system","content":"更新的设定"}}
    以下是你昨天写的日记：
    {diary}
    """
    message = [
        {"role": "user", "content": self_update_prompt.format(diary=diary, current_setting=current_setting)}
    ]
    # 按照对话历史自我更新，感觉效果不太好
    # self_update_prompt = """
    # 现在，请开始你的自我更新。请根据我们昨天的对话内容，更新你的设定与想要记住的事。注意：
    # 1. 有选择地进行更新，因为你的记忆有限，请你自己进行取舍，选择记住那些又遗忘哪些。
    # 2. 你目前的设定是：{current_setting}
    # 3. 请按照json格式输出更新的设定，格式为：{{"role":"system","content":"更新的设定"}}
    # 以下是我们昨天的对话内容：
    # {history}
    # """
    # message = [
    #     {"role": "user", "content": self_update_prompt.format(history=history,current_setting=current_setting)}
    # ]
    print(message)
    response = get_chat_response(message)
    print(response)
    return response

# 仅保留时间戳、角色和内容
def strip_history(history):
    return [{"role": item["role"], "timestamp": item["timestamp"], "content": item["content"]} for item in history]
