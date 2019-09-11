#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import wx.adv
import time;
import base64;
import hashlib;
import random;
import json;
import string;
import os;
import urllib;
from urllib.parse import quote;
from urllib import request;

class BaseClass:
    def __init__(self, url):
        """
        :param url:api的访问地址
        """
        self.URL = url;
        self.APP_ID = '2121530222';  
        self.APP_KEY = 'FBXGGv1UCaXx8FwZ'; 
        self.params = {
            'app_id' : self.APP_ID,
            'time_stamp' : None,
            'nonce_str' : None,
        };
        self.result = None;

    def __get_sign(self):
        time_stamp = int(time.time());
        nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
        self.params['time_stamp'] = time_stamp;
        self.params['nonce_str'] = nonce_str;
        before_sign = '';
        for key in sorted(self.params):
            before_sign += f'{key}={quote(str(self.params[key]).encode("utf-8"))}&';
        before_sign += f"app_key={self.APP_KEY}";
        sign = hashlib.md5(before_sign.encode("utf-8")).hexdigest().upper();
        self.params["sign"] = sign;

    def get_result(self):
        self.__get_sign();
        params = urllib.parse.urlencode(self.params).encode("utf-8");
        req = request.Request(url=self.URL, data=params);
        count = 0;
        while True:
            try:
                count += 1;
                self.result = request.urlopen(req, timeout=10);
                break;
            except Exception as e:
                print(e)
                print(f"连接超时，正在进行第{str(count)}次重连")
                if count <= 3:
                    continue;
                else:
                    break;

    def do_result(self):
        pass;

    def run(self):
        pass;

# 使用腾讯语音合成api
class TencentVoice(BaseClass):

    def __init__(self, text,audio_path, sound_choice=2, sound_speed=0):
        super(TencentVoice, self).__init__('https://api.ai.qq.com/fcgi-bin/aai/aai_tta');
        self.TEXT = text;
        self.audio_path = audio_path;
        self.params['model_type'] = sound_choice;  # 语音 0~2。0：女。1：女英文。2：男
        self.params['speed'] = sound_speed;  # 语速 -2:0.6倍，-1:0.8倍, 0：正常， 1:1.2倍，2:1.5倍
        self.msg = 'ok'
        self.file_name = 'err'

    def deal_text(self):
        if len(self.TEXT.encode("utf-8")) > 300:
            raise ValueError("text参数长度超出限制，限制utf8下300个字节")
        if isinstance(self.TEXT, str):
            self.params["text"] = self.TEXT;
            self.do_result(self.TEXT);
        elif isinstance(self.TEXT, list):
            for text in self.TEXT:
                if len(text.encode("utf-8")) > 300:
                    raise ValueError("text参数长度超出限制，限制utf8下300个字节");
                else:
                    self.params["text"] = text;
                    self.do_result(text);

    def do_result(self, text):
        self.get_result();
        # print(self.params)
        res = json.loads(self.result.read().decode("utf-8"));
        if not res["msg"] == "ok":
            self.msg = "语音合成出错："+res["msg"];
            self.file_name = 'err'
        else:
            voice_data = base64.decodestring(bytes(res["data"]["voice"].encode("utf-8")));
            if voice_data:
                self.file_name = self.audio_path+"\\" + str(time.time()) + ".mp3";
                with open(self.file_name, "wb") as f:
                    f.write(voice_data);

    def play_audio(self):
        if not self.file_name =='err':
            os.system(self.file_name);

    def run(self):
        self.deal_text();

# 使用腾讯智能闲聊api
class TencetChat(BaseClass):
    def __init__(self, question):
        super(TencetChat, self).__init__("https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat");
        self.params["session"] = "10000"
        self.question = question;

    def deal_question(self):
        if not isinstance(self.question, str):
            raise TypeError(f"question参数必须是 ‘str’ 类型的，不能是 ‘{type(self.question)}’ 类型的！！！");
        else:
            if len(self.question.encode("utf-8")) > 300:
                raise ValueError("question参数的长度必须小于300个字节（utf-8格式下）")
            else:
                self.params["question"] = self.question;
                # print(self.params)
                self.do_result();

    def do_result(self):
        self.get_result();
        if self.result:
            res = json.loads(self.result.read().decode("utf-8"));
            #print(res)
            if not res["msg"] == "ok":
                self.answer = "我好像出错了："+res["msg"];
            else:
                self.answer = res["data"]["answer"];
        else:
            self.answer="我尝试了4次，但还是失败了，只能说我尽力了。";

    def run(self):
        self.deal_question();
		
# 使用腾讯情感分析api
class Tencetpolar(BaseClass):
    def __init__(self, text):
        super(Tencetpolar, self).__init__("https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar");
        self.text = text;

    def deal_text(self):
        if not isinstance(self.text, str):
            raise TypeError(f"question参数必须是 ‘str’ 类型的，不能是 ‘{type(self.text)}’ 类型的！！！");
        else:
            if len(self.text.encode("utf-8")) > 300:
                raise ValueError("question参数的长度必须小于300个字节（utf-8格式下）")
            else:
                self.params["text"] = self.text;
                # print(self.params)
                self.do_result();

    def do_result(self):
        self.get_result();
        if self.result:
            res = json.loads(self.result.read().decode("utf-8"));
            #print(res)
            if not res["msg"] == "ok":
                self.polar = "我好像出错了："+res["msg"];
                self.confd = " ";
            else:
                self.polar = res["data"]["polar"];
                self.confd = res["data"]["confd"];
        else:
            self.polar="我尝试了4次，但还是失败了，只能说我尽力了。";
            self.confd=" ";
    def run(self):
        self.deal_text();
		
def create(parent):
    return Frame1(parent)

[wxID_FRAME1, 
 wxID_FRAME1SASHLAYOUTWINDOW1, 
 wxID_FRAME1TEXTRETURN,
 wxID_FRAME1PANEL1,
 wxID_FRAME1CHECKBOX_POLAR, 
 wxID_FRAME1CHECKBOX_VOICE, 
 wxID_FRAME1RADIOBUTTON1, 
 wxID_FRAME1RADIOBUTTON2, 
 wxID_FRAME1BTN_CLEAR, 
 wxID_FRAME1BTN_SEND, 
 wxID_FRAME1TEXTINPUT
] = [wx.NewId() for _init_ctrls in range(11)]

class Frame1(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(438, 55), size=wx.Size(810, 704),
              style= wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX), title=u'Alpha-C')
        self.SetClientSize(wx.Size(810, 665))
        self.Bind(wx.EVT_SIZE, self.OnFrame1Size)

        self.sashLayoutWindow1 = wx.adv.SashLayoutWindow(id=wxID_FRAME1SASHLAYOUTWINDOW1,
              name='sashLayoutWindow1', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(800, 500), style=wx.CLIP_CHILDREN|wx.adv.SW_3D)
        self.sashLayoutWindow1.SetAlignment(wx.adv.LAYOUT_TOP)
        self.sashLayoutWindow1.SetOrientation(wx.adv.LAYOUT_HORIZONTAL)
        self.sashLayoutWindow1.SetSashVisible(wx.adv.SASH_BOTTOM, True)
        self.sashLayoutWindow1.SetDefaultSize(wx.Size(800, 500))

        self.textReturn = wx.TextCtrl(id=wxID_FRAME1TEXTRETURN,
              name=u'textReturn', parent=self.sashLayoutWindow1, pos=wx.Point(0, 0),
              size=wx.Size(800, 500), style=wx.TE_MULTILINE, value='')

        self.panel1 = wx.Panel(id=wxID_FRAME1PANEL1, name='panel1', parent=self,
              pos=wx.Point(0, 500), size=wx.Size(800, 200),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetMinSize(wx.Size(800, 200))

        self.checkBox_voice = wx.CheckBox(self.panel1, -1, u'\u8bed\u97f3\u804a\u5929', pos=(300, 14))

        self.radioButton1 = wx.RadioButton(id=wxID_FRAME1RADIOBUTTON1,
              label=u'\u7537', name='radioButton1', parent=self.panel1,
              pos=wx.Point(380, 14), size=wx.Size(32, 16), style=0)
        self.radioButton1.SetValue(True)
        self.radioButton1.Enable(True)
        self.radioButton1.Show(True)
        self.radioButton1.Bind(wx.EVT_RADIOBUTTON,
              self.OnRadioButton1Radiobutton, id=wxID_FRAME1RADIOBUTTON1)

        self.radioButton2 = wx.RadioButton(id=wxID_FRAME1RADIOBUTTON2,
              label=u'\u5973', name='radioButton2', parent=self.panel1,
              pos=wx.Point(420, 14), size=wx.Size(32, 16), style=0)
        self.radioButton2.SetValue(True)
        self.radioButton2.Bind(wx.EVT_RADIOBUTTON,
              self.OnRadioButton2Radiobutton, id=wxID_FRAME1RADIOBUTTON2)

        self.checkBox_polar = wx.CheckBox(self.panel1, -1, u'\u60c5\u7eea\u5206\u6790', pos=(500, 14))

        self.btn_clear = wx.Button(id=wxID_FRAME1BTN_CLEAR,
              label=u'\u6e05\u7a7a', name=u'btn_clear',
              parent=self.panel1, pos=wx.Point(600, 12), size=wx.Size(75, 24),
              style=0)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.Onbtn_clearButton,
              id=wxID_FRAME1BTN_CLEAR)

        self.btn_send = wx.Button(id=wxID_FRAME1BTN_SEND,
              label=u'\u53d1\u9001', name=u'btn_test_posion',
              parent=self.panel1, pos=wx.Point(700, 12), size=wx.Size(75, 24),
              style=0)
        self.btn_send.Bind(wx.EVT_BUTTON, self.Onbtn_sendButton,
              id=wxID_FRAME1BTN_SEND)
		
        self.textInput = wx.TextCtrl(id=wxID_FRAME1TEXTINPUT,
              name=u'textInput', parent=self.panel1, pos=wx.Point(0, 50),
              size=wx.Size(810, 115), style=wx.TE_MULTILINE, value='')
			  
    def __init__(self, parent):
        self._init_ctrls(parent)
        self.textReturn.AppendText('欢迎使用智能闲聊，下面开始聊天吧\n')
        self.sound_choice = 0

    def doLayout(self):
        wx.adv.LayoutAlgorithm().LayoutWindow(self, self.panel1)
        self.panel1.Refresh()
		
    def OnFrame1Size(self, event):
        self.doLayout()
        event.Skip()

    def Onbtn_clearButton(self, event):
        self.textReturn.Clear()
        event.Skip()
		
    def OnRadioButton1Radiobutton(self, event):
        self.sound_choice = 0 # 语音 0~2。0：女。1：女英文。2：男
        event.Skip()

    def OnRadioButton2Radiobutton(self, event):
        self.sound_choice = 2
        event.Skip()
		
    def Onbtn_sendButton(self, event):
        use_voice=self.checkBox_voice.IsChecked()
        use_polar=self.checkBox_polar.IsChecked()
        question = self.textInput.Value;
        if use_polar:
            t_polar = Tencetpolar(question);
            t_polar.run();
            polar = t_polar.polar;
            confd = t_polar.confd;
            if polar == -1:
                strpolar ='情绪:负面;程度:'+str(confd);
            elif polar == 0:
                strpolar ='情绪:中性;程度:'+str(confd);
            else:
                strpolar ='情绪:正面;程度:'+str(confd);

        t_chat = TencetChat(question);
        t_chat.run();
        answer = t_chat.answer;
        self.textReturn.AppendText('我：'+question+'\n');
        if use_polar:
            self.textReturn.AppendText(strpolar+'\n');
        self.textReturn.AppendText('智能闲聊：'+answer+'\n');	
        self.textInput.Clear();
        if use_voice:
            audiopath = os.getcwd()
            print(audiopath);
            t_voice = TencentVoice(answer,audio_path=audiopath,sound_choice= self.sound_choice,sound_speed=-1);
            t_voice.run();
            if not t_voice.msg == "ok":
                self.textReturn.AppendText(t_voice.msg+'\n');
            else:
                t_voice.play_audio();

        event.Skip()
