# encoding:utf-8

import json
import os

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *

from .lib.WordsSearch import WordsSearch


@plugins.register(
    name="Banwords",
    desire_priority=100,
    hidden=True,
    desc="判断消息中是否有敏感词、决定是否回复。",
    version="1.0",
    author="lanvent",
)
class Banwords(Plugin):
    def __init__(self):
        super().__init__()
        try:
            curdir = os.path.dirname(__file__)
            config_path = os.path.join(curdir, "config.json")
            conf = None
            if not os.path.exists(config_path):
                conf = {"action": "replace"}
                with open(config_path, "w") as f:
                    json.dump(conf, f, indent=4)
            else:
                with open(config_path, "r") as f:
                    conf = json.load(f)
            self.searchr = WordsSearch()
            self.action = conf["action"]
            banwords_path = os.path.join(curdir, "banwords.txt")
            with open(banwords_path, "r", encoding="utf-8") as f:
                words = []
                for line in f:
                    word = line.strip()
                    if word:
                        words.append(word)
            self.searchr.SetKeywords(words)
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            if conf.get("reply_filter", True):
                self.handlers[Event.ON_DECORATE_REPLY] = self.on_decorate_reply
                self.reply_action = conf.get("reply_action", "replace")
            logger.info("[Banwords] inited")
        except Exception as e:
            logger.warn("[Banwords] init failed, ignore or see https://github.com/zhayujie/chatgpt-on-wechat/tree/master/plugins/banwords .")
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
            ContextType.IMAGE_CREATE,
        ]:
            return
        try:
            # 提问不处理敏感词，回复替换敏感词
            # content = e_context["context"].content
            # logger.debug("[Banwords] on_handle_context. content: %s" % content)
            # if self.action == "ignore":
            #     f = self.searchr.FindFirst(content)
            #     if f:
            #         logger.info("[Banwords] %s in message" % f["Keyword"])
            #         reply = Reply(ReplyType.INFO, "发言中包含敏感词，请文明用语，并遵循互联网的法律法规，谢谢! \n")
            #         e_context["reply"] = reply
            #         e_context.action = EventAction.BREAK_PASS
            #         return
            # elif self.action == "replace":
            #     if self.searchr.ContainsAny(content):
            #         # reply = Reply(ReplyType.INFO, "发言中包含敏感词，请更改后重试: \n" + self.searchr.Replace(content))
            #         # e_context["reply"] = reply
            #         # e_context.action = EventAction.BREAK_PASS
            #         e_context["context"].content = self.searchr.Replace(content)
            #         return
            return
        except Exception as e:
            logger.error("[Banwords] on_handle_context ocur error")
            return

    def on_decorate_reply(self, e_context: EventContext):
        if e_context["reply"].type not in [ReplyType.TEXT]:
            return

        try:
            reply = e_context["reply"]
            content = reply.content
            if self.reply_action == "ignore":
                f = self.searchr.FindFirst(content)
                if f:
                    logger.info(f"[Banwords] org replay:{content}")
                    logger.info("[Banwords] %s in reply" % f["Keyword"])
                    e_context["reply"] = Reply(ReplyType.INFO, "回复中包含敏感词，麻烦换一个问法，抱歉了。 \n")
                    e_context.action = EventAction.BREAK_PASS
                    return
            elif self.reply_action == "replace":
                if self.searchr.ContainsAny(content):
                    # reply = Reply(ReplyType.INFO, "已替换回复中的敏感词: \n" + self.searchr.Replace(content))
                    logger.info(f"[Banwords] org replay:{content}")
                    reply = Reply(ReplyType.TEXT,self.searchr.Replace(content))
                    e_context["reply"] = reply
                    e_context.action = EventAction.CONTINUE
                    return
        except Exception as e:
            logger.error("[Banwords] on_decorate_reply ocur error",e)
            e_context["reply"] = None
            e_context.action = EventAction.BREAK_PASS
            return

    def get_help_text(self, **kwargs):
        return "过滤消息中的敏感词。"
