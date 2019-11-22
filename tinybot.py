# -*- coding: utf-8 -*-
""" Tinybot by Nortxort (https://github.com/nortxort/tinybot-rtc) """
""" Modified by Smokey """

import time
import logging
import threading
import os
import pinylib

from page import privacy
from util import tracklist
from apis import youtube, other, locals_


import random
from random import randint

import pickledb

__version__ = '2.1'

log = logging.getLogger(__name__)

joind_time = 0
joind_count = 0
bad_nick = 0
autoban_time = 0
autoban_count = 0
newnick = 0
ban_time = 0
spam = 0
spammer = 0
lastmsgs = []


sword = 0
flower = 0

answer_A = ["A", "a"]
answer_B = ["B", "b"]
answer_C = ["C", "c"]
yes = ["Y", "y", "yes"]
no = ["N", "n", "no"]



# Random password words
_KEYWORDS = ["fob", "fobcity", "terima", "halal", "haram", "roses", ]


class TinychatBot(pinylib.TinychatRTCClient):
    privacy_ = None
    timer_thread = None
    playlist = tracklist.PlayList()
    search_list = []
    is_search_list_yt_playlist = False


    announce = 0
    announceCheck = 0

    tokers = []
    toke_start = 0
    toke_end = 0
    toke_mode = False
    toker = None
    
    fishers = []
    fish_start = 0
    fish_end = 0
    fish_mode = False
    fisher = None
    catch = []
    
    hunters = []
    hunt_start = 0
    hunt_end = 0
    hunt_mode = False
    hunter = None
    hunted = []
    

    @property
    def config_path(self):
        """ Returns the path to the rooms configuration directory. """
        return pinylib.CONFIG.CONFIG_PATH + self.room_name + '/'

    global lockdown
    global userdb
    global db

    lockdown = False

    userdb = pinylib.CONFIG.CONFIG_PATH + pinylib.CONFIG.ROOM + '/' + 'user.db'
    db = pickledb.load(userdb, False)

    def isWord(self, word):

        VOWELS = "aeiou"
        PHONES = ['sh', 'ch', 'ph', 'sz', 'cz', 'sch', 'rz', 'dz']
        prevVowel = False


        if word:
            consecutiveVowels = 0
            consecutiveConsonents = 0
            for idx, letter in enumerate(word.lower()):
                vowel = True if letter in VOWELS else False

                if idx:
                    prev = word[idx - 1]
                    if prev in VOWELS:
                        prevVowel = True
                    if not vowel and letter == 'y' and not prevVowel:
                        vowel = True

                if prevVowel != vowel:
                    consecutiveVowels = 0
                    consecutiveConsonents = 0

                if vowel:
                    consecutiveVowels += 1
                else:
                    consecutiveConsonents += 1

                if consecutiveVowels >= 3 or consecutiveConsonents > 3:
                    return False

                if consecutiveConsonents == 3:
                    subStr = word[idx - 2:idx + 1]
                    if any(phone in subStr for phone in PHONES):
                        consecutiveConsonents -= 1
                        continue
                    return False

        return True

    def on_joined(self, client_info):
        """
        Received when the client have joined the room successfully.

        :param client_info: This contains info about the client, such as user role and so on.
        :type client_info: dict
        """
        log.info('client info: %s' % client_info)
        self.client_id = client_info['handle']
        self.is_client_mod = client_info['mod']
        self.is_client_owner = client_info['owner']
        client = self.users.add(client_info)
        client.user_level = 3
        self.console_write(pinylib.COLOR[
                           'bright_green'], '[Bot] connected as %s:%s' % (client.nick, client.id))

        threading.Thread(target=self.options).start()

        if not os.path.exists(userdb):
            
            db = pickledb.load(userdb, False)
            db.dcreate('users')
            db.dcreate('badwords')
            db.dcreate('badnicks')
            
            db.dcreate('gamers')
            db.dcreate('fishing_poles')
            db.dcreate('weapons')
            
            db.dump()
            
            self.console_write(pinylib.COLOR['bright_green'], '[DB] Created')
        
        else:
            db = pickledb.load(userdb, False)
            self.console_write(pinylib.COLOR['bright_green'], '[DB] Loaded')
       
    def on_join(self, join_info):
        """
        Received when a user joins the room.

        :param join_info: This contains user information such as role, account and so on.
        :type join_info: dict
        """

        global joind_time
        global joind_count
        global autoban_time
        global lockdown
        global bad_nick
        global db 

        time_join = time.time()

        log.info('user join info: %s' % join_info)
        _user = self.users.add(join_info)


        if self.nick_check(_user.nick):
            if pinylib.CONFIG.B_USE_KICK_AS_AUTOBAN:
                self.send_kick_msg(_user.id)
            else:
                self.send_ban_msg(_user.id)
                self.console_write(pinylib.COLOR['cyan'], '[Security] Banned: Nick %s' % (_user.nick))

        if _user.account:
          
            if _user.is_owner:
                _user.user_level = 1 # account owner
                self.console_write(pinylib.COLOR['red'], '[User] Room Owner %s:%d:%s' %
                                   (_user.nick, _user.id, _user.account))
            elif _user.is_mod:
                _user.user_level = 3 # mod
                self.console_write(pinylib.COLOR['bright_red'], '[User] Moderator %s:%d:%s' %
                                   (_user.nick, _user.id, _user.account))


                     
            if db.dexists('users', _user.account):
           
                _level = self.user_check(_user.account)
              
                if _level == 4 and not _user.is_mod:
                      _user.user_level = _level # chatmod

                if _level == 5 and not _user.is_mod:
                      _user.user_level = _level # whitelist 

                if _level == 2: # overwrite mod to chatadmin
                      _user.user_level = _level

                self.console_write(pinylib.COLOR['bright_red'], '[User] Found, level(%s)  %s:%d:%s' % (_user.user_level, _user.nick, _user.id, _user.account))
            
            else:
                if not _user.user_level:
                    _user.user_level = 6 # account not verified
                    self.console_write(pinylib.COLOR['bright_red'], '[User] Not verified %s:%d:%s' % (
                        _user.nick, _user.id, _user.account))

            if self.user_check(_user.account) == 9 and self.is_client_mod:
                if pinylib.CONFIG.B_USE_KICK_AS_AUTOBAN:
                     self.send_kick_msg(_user.id)
                else:
                    self.send_ban_msg(_user.id)
                    self.console_write(
                        pinylib.COLOR['cyan'], '[Security] Banned: Account %s' % (_user.account))
            else:

                tc_info = pinylib.apis.tinychat.user_info(_user.account)
                  
                if tc_info is not None:
                    _user.tinychat_id = tc_info['tinychat_id']
                    _user.last_login = tc_info['last_active']

        else:
            _user.user_level = 7 # guest
            self.console_write(
                pinylib.COLOR['bright_red'], '[User] Guest %s:%d' % (_user.nick, _user.id))

        if lockdown and autoban_time != 0:
            if time_join - 240 > autoban_time:
                if lockdown == 1:
                    soft = 1
                    self.do_lockdown(soft)
                    autoban_time = 0
                    bad_nick = 0
                    self.console_write(
                        pinylib.COLOR['cyan'], '[Security] Lockdown Mode Reset')
        else:

            maxtime = 7
            maxjoins = 8

            if joind_time == 0:
                joind_time = time.time()
                joind_count += 1

            elif time_join - joind_time > maxtime:
                joind_count = 0
                joind_time = 0
                bad_nick = 0

            elif joind_count > maxjoins:

                soft = 0
                self.do_lockdown(soft)
                autoban_time = time_join
                self.console_write(
                    pinylib.COLOR['cyan'], '[Security] Lockdown started')
            else:
                joind_count += 1

            if not self.isWord(_user.nick):
                bad_nick += 1

            if bad_nick > 3:
                time.sleep(1.0)

                self.send_ban_msg(_user.id)
                self.console_write(pinylib.COLOR[
                                   'cyan'], '[Security] Randomized Nick Banned: Nicks %s' % (_user.nick))

        if not pinylib.CONFIG.B_ALLOW_GUESTS:
            if _user.user_level == 7:
                self.send_ban_msg(_user.id)
                self.console_write(pinylib.COLOR[
                                   'cyan'], '[Security] %s was banned on no guest mode' % (_user.nick))

        self.console_write(pinylib.COLOR['cyan'], '[User] %s:%d joined the room. (%s)' % (
            _user.nick, _user.id, joind_count))
        threading.Thread(target=self.welcome, args=(_user.id,)).start()

    def welcome(self, uid):
        time.sleep(1)
        _user = self.users.search(uid)
        _level = self.user_check(_user.account)
        if _user is not None:
            if pinylib.CONFIG.B_ALLOW_GUESTS:
                if pinylib.CONFIG.B_GREET and _user is not None:
                    if not _user.nick.startswith('guest-'):
                        if _user.account == 'smokeyllama':
                            pass
                            self.send_chat_msg(' Yo its %s (%s)! he\'s dope.' % (_user.nick, _user.account))
                        elif _user.user_level < 3:
                            pass
                            self.send_chat_msg(' ❢👑𝙊𝙒𝙉𝙀𝙍👑❢ \n ---👋𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘽𝙖𝙘𝙠 𝙃𝙤𝙢𝙚')
                        elif _user.user_level < 4:
                            pass
                            self.send_chat_msg(' 👑𝙈𝙤𝙙❢ \n 👋𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙩𝙝𝙚 𝓒𝓸𝓯𝓯𝓮𝓮𝓟𝓸𝓽❢ \n 🧟‍♂️ %s (%s) ' % (_user.nick, _user.account))
                        elif _level == 5 or _level == 4:
                            pass
                            self.send_chat_msg(' ✔️ 𝙑𝙚𝙧𝙞𝙛𝙞𝙚𝙙 \n 👋𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙩𝙝𝙚 𝓒𝓸𝓯𝓯𝓮𝓮𝓟𝓸𝓽❢ \n 🧟‍♂️ %s (%s)' % (_user.nick, _user.account))
                        elif _user.user_level == 5:
                            pass
                            self.send_chat_msg(' 👋𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙩𝙝𝙚 𝓒𝓸𝓯𝓯𝓮𝓮𝓟𝓸𝓽❢ \n 🧟‍♂️ %s (%s)' % (_user.nick, _user.account))

                        elif _user.user_level == 6:
                            #self.send_private_msg(_user.id, 'Welcome to %s - ask to have your account verified.' % (self.room_name))
                            self.send_chat_msg('👋𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝓒𝓸𝓯𝓯𝓮𝓮𝓟𝓸𝓽❢ \n 🧟‍♂️ %s (%s) \n 😀𝙀𝙣𝙟𝙤𝙮❢' % (_user.nick, _user.account))
                            
                        elif _user.user_level == 7:
                            #self.send_private_msg(_user.id, 'Welcome to %s - we suggest making an account, personal info trolling or sexual harassment will not be tolerated.' % (self.room_name))
                            self.send_chat_msg('👋𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝓒𝓸𝓯𝓯𝓮𝓮𝓟𝓸𝓽❢ \n 🧟‍♂️ %s. 😒𝙃𝙢𝙢𝙢, 𝙄𝙩 𝙎𝙚𝙚𝙢𝙨 𝙔𝙤𝙪𝙧𝙚 𝙉𝙤𝙩 𝙎𝙞𝙜𝙣𝙚𝙙 𝙄𝙣.' % (_user.nick))
                               
    def on_quit(self, uid):
        time.sleep(1)
        _user = self.users.search(uid)

        if _user is not None:
            if pinylib.CONFIG.B_ALLOW_GUESTS:
                if pinylib.CONFIG.B_FAREWELL and _user is not None:
                    if not _user.nick.startswith('guest-'):
                        if _user.user_level < 4:
                            pass
                            self.send_chat_msg(' 👑𝙈𝙤𝙙❢ \n 👋 %s (%s) left the room' % (_user.nick, _user.account))
                        elif _user.user_level == 5:
                            self.send_chat_msg('👋 %s (%s) left the room!' % (_user.nick, _user.account))
                    
    def on_pending_moderation(self, pending):
        _user = self.users.search(pending['handle'])
        if _user is not None:
            if self.user_check(_user.account) == 5 or self.user_check(_user.account) == 4:
                self.send_cam_approve_msg(_user.id)
            else:
                _user.is_waiting = True
                self.send_chat_msg(
                    '%s is waiting in the greenroom.' % (_user.nick))

    def do_lockdown(self, soft):

        global password
        global lockdown

        if self.is_client_owner:
            if soft:
                password = None
            else:
                password = self.do_create_password()

            if not self.privacy_.set_guest_mode():
                self.privacy_.set_room_password(password)
                lockdown = True
                if soft:
                    self.send_chat_msg('Lockdown - no guests allowed.')
                else:
                    self.send_chat_msg(
                        'Lockdown - tmp password is: %s' % (password))
            else:
                password = None
                self.privacy_.set_room_password(password)
                lockdown = False
                self.send_chat_msg(
                    '%s is open to the public again.' % (self.room_name))

        else:
            if not pinylib.CONFIG.B_ALLOW_GUESTS:
                lockdown = False
                self.do_guests()
                self.send_chat_msg(
                    '%s is open to the public again.' % (self.room_name))

            else:
                self.do_guests()
                self.send_chat_msg('Lockdown - no guests allowed.')

    def on_nick(self, uid, nick):
        """
        Received when a user changes nick name.

        :param uid: The ID (handle) of the user.
        :type uid: int
        :param nick: The new nick name.
        :type nick: str
        """
        _user = self.users.search(uid)
        old_nick = _user.nick
        _user.nick = nick

        if uid != self.client_id:
            if self.nick_check(_user.nick):
                if pinylib.CONFIG.B_USE_KICK_AS_AUTOBAN:
                    self.send_kick_msg(uid)
                else:
                    self.send_ban_msg(uid)

                self.console_write(pinylib.COLOR['bright_cyan'], '[User] %s:%s Changed nick to: %s' %
                                   (old_nick, uid, nick))

    def on_yut_play(self, yt_data):
        """
        Received when a youtube gets started or time searched.

        This also gets received when the client starts a youtube, the information is 
        however ignored in that case.

        :param yt_data: The event information contains info such as the ID (handle) of the user 
        starting/searching the youtube, the youtube ID, youtube time and so on.
        :type yt_data: dict
        """
        user_nick = 'n/a'
        if 'handle' in yt_data:
            if yt_data['handle'] != self.client_id:
                _user = self.users.search(yt_data['handle'])
                user_nick = _user.nick

        if self.playlist.has_active_track:
            self.cancel_timer()

        if yt_data['item']['offset'] == 0:
            _youtube = youtube.video_details(yt_data['item']['id'], False)
            self.playlist.start(user_nick, _youtube)
            self.timer(self.playlist.track.time)
            self.console_write(pinylib.COLOR['bright_magenta'], '[Media] %s started youtube video (%s)' %
                               (user_nick, yt_data['item']['id']))
        elif yt_data['item']['offset'] > 0:
            if user_nick == 'n/a':
                _youtube = youtube.video_details(yt_data['item']['id'], False)
                self.playlist.start(user_nick, _youtube)
                offset = self.playlist.play(yt_data['item']['offset'])
                self.timer(offset)
            else:
                offset = self.playlist.play(yt_data['item']['offset'])
                self.timer(offset)
                self.console_write(pinylib.COLOR['bright_magenta'], '[Media] %s searched the youtube video to: %s' %
                                   (user_nick, int(round(yt_data['item']['offset']))))

    def on_yut_pause(self, yt_data):
        """
        Received when a youtube gets paused or searched while paused.

        This also gets received when the client pauses or searches while paused, the information is 
        however ignored in that case.

        :param yt_data: The event information contains info such as the ID (handle) of the user 
        pausing/searching the youtube, the youtube ID, youtube time and so on.
        :type yt_data: dict
        """
        if 'handle' in yt_data:
            if yt_data['handle'] != self.client_id:
                _user = self.users.search(yt_data['handle'])
                if self.playlist.has_active_track:
                    self.cancel_timer()
                self.playlist.pause()
                self.console_write(pinylib.COLOR['bright_magenta'], '[Media] %s paused the video at %s' %
                                   (_user.nick, int(round(yt_data['item']['offset']))))

    def message_handler(self, msg):
        """
        A basic handler for chat messages.

        Overrides message_handler in pinylib
        to allow commands.

        :param msg: The chat message.
        :type msg: str
        
        User Levels
        
        7 : Not Signed In
        5 : Signed In
        3 : MOD
        
        Script Levels
        
        0 : All
        5 : Verified/On File
        
        """
        prefix = pinylib.CONFIG.B_PREFIX

        if msg.startswith(prefix):
            parts = msg.split(' ')
            cmd = parts[0].lower().strip()
            cmd_arg = ' '.join(parts[1:]).strip()

            _user = self.users.search_by_nick(self.active_user.nick)
            _level = self.user_check(_user.account)

            
            if _user.user_level < 4:
                if cmd == prefix + 'chatmod':
                    self.do_chatmod(cmd_arg)
                elif cmd == prefix + 'rmchatmod':
                    self.do_remove_chatmod(cmd_arg)
                elif cmd == prefix + 'demod':
                    self.do_deop_user(cmd_arg)
                elif cmd == prefix + 'noguest':
                    self.do_guests()
                elif cmd == prefix + 'lockdown':
                    self.do_lockdown(1)
                elif cmd == prefix + 'lockup':
                    self.do_lockdown(0)

            if _user.user_level == 2:


                if cmd == prefix + 'chatadmin':
                    self.do_chatadmin(cmd_arg)

                if self.is_client_owner:

                    if cmd == prefix + 'p2t':
                        threading.Thread(target=self.do_push2talk).start()
                    elif cmd == prefix + 'greet':
                        self.do_greet()
                    elif cmd == prefix == 'kb':
                        self.do_kick_as_ban()
                    elif cmd == prefix + 'reboot':
                        self.do_reboot()
                    elif cmd == prefix + 'dir':
                        threading.Thread(target=self.do_directory).start()
                    elif cmd == prefix + 'addmod':
                        threading.Thread(target=self.do_make_mod,
                                         args=(cmd_arg,)).start()
                    elif cmd == prefix + 'removemod':
                        threading.Thread(
                            target=self.do_remove_mod, args=(cmd_arg,)).start()

            if _user.user_level < 5 or _level == 4:

                if cmd == prefix + 'mod':
                    self.do_op_user(cmd_arg)
                elif cmd == prefix + 'who':
                    self.do_user_info(cmd_arg)
                if cmd == prefix + 'rmvgamer':
                    self.do_remove_gamer(cmd_arg)
                elif cmd == prefix + 'bruh':
                    self.do_verified(cmd_arg)
                elif cmd == prefix + 'rmv':
                    self.do_remove_verified(cmd_arg)
                elif cmd == prefix + 'clr':
                    self.do_clear()
                elif cmd == prefix + 'forgive':
                    threading.Thread(target=self.do_forgive,
                                     args=(cmd_arg,)).start()
                elif cmd == prefix + 'kick':
                    threading.Thread(target=self.do_kick,
                                     args=(cmd_arg,)).start()
                elif cmd == prefix + 'ban':
                    threading.Thread(target=self.do_ban,
                                     args=(cmd_arg,)).start()
                elif cmd == prefix + 'uinfo':
                    self.do_user_info(cmd_arg)
                elif cmd == prefix + 'cam':
                    self.do_cam_approve(cmd_arg)
                elif cmd == prefix + 'close':
                    self.do_close_broadcast(cmd_arg)
                elif cmd == prefix + 'badn':
                    self.do_bad_nick(cmd_arg)
                elif cmd == prefix + 'rmbadn':
                    self.do_remove_bad_nick(cmd_arg)
                elif cmd == prefix + 'banw':
                    self.do_bad_string(cmd_arg)
                elif cmd == prefix + 'rmw':
                    self.do_remove_bad_string(cmd_arg)
                elif cmd == prefix + 'bada':
                    self.do_bad_account(cmd_arg)
                elif cmd == prefix + 'rmbada':
                    self.do_remove_bad_account(cmd_arg)

        
            if _user.user_level < 5 or _level == 5 or _level == 4:
                if cmd == prefix + 'fish':
                    self.do_fish()
                elif cmd == prefix + 'hunt':
                    self.do_hunt()
                    
                elif cmd == prefix + 'store':
                    self.open_shop()
                elif cmd == prefix + 'shop':
                    self.open_shop()
                    
                elif cmd == prefix + 'pole_shop':
                    self.open_shop_poles()
                elif cmd == prefix + 'pole':
                    self.buy_pole(cmd_arg)
                elif cmd == prefix + 'pole_stats':
                    self.pole_stats()
                    
                elif cmd == prefix + 'sword_shop':
                    self.open_shop_swords()
                elif cmd == prefix + 'sword':
                    self.buy_sword(cmd_arg)
                elif cmd == prefix + 'sword_stats':
                    self.sword_stats()
                    
                elif cmd == prefix + 'bow_shop':
                    self.open_shop_bows()
                elif cmd == prefix + 'bow':
                    self.buy_bow(cmd_arg)
                elif cmd == prefix + 'bow_stats':
                    self.bow_stats()

                elif cmd == prefix + 'bet':
                    self.do_bet(cmd_arg, cmd_arg)
                    
                elif cmd == prefix + 'advtime':
                    self.do_advtime()
                    
                elif cmd == prefix + 'scriptlvl':
                    self.do_script_level()
                elif cmd == prefix + 'lvl':
                    self.do_level()
                    
                elif cmd == prefix + 'skip':
                    self.do_skip()
                elif cmd == prefix + 'media':
                    self.do_media_info()
                elif cmd == prefix + 'yt':
                    threading.Thread(target=self.do_play_youtube,
                                     args=(cmd_arg,)).start()
                elif cmd == prefix + 'stan':
                    threading.Thread(target=self.do_play_youtube,
                                     args=('AHukwv_VX9A',)).start()
                    self.do_stan()
                elif cmd == prefix + 'yts':
                    threading.Thread(target=self.do_youtube_search,
                                     args=(cmd_arg,)).start()
                elif cmd == prefix + 'del':
                    self.do_delete_playlist_item(cmd_arg)
                elif cmd == prefix + 'replay':
                    self.do_media_replay()
                elif cmd == prefix + 'play':
                    self.do_play_media()
                elif cmd == prefix + 'pause':
                    self.do_media_pause()
                elif cmd == prefix + 'seek':
                    self.do_seek_media(cmd_arg)
                elif cmd == prefix + 'stop':
                    self.do_close_media()
                elif cmd == prefix + 'reset':
                    self.do_clear_playlist()
                elif cmd == prefix + 'next':
                    self.do_next_tune_in_playlist()
                elif cmd == prefix + 'playlist':
                    self.do_playlist_info()
                elif cmd == prefix + 'pyts':
                    self.do_play_youtube_search(cmd_arg)
                elif cmd == prefix + 'pls':
                    threading.Thread(target=self.do_youtube_playlist_search,
                                     args=(cmd_arg,)).start()
                elif cmd == prefix + 'plp':
                    threading.Thread(target=self.do_play_youtube_playlist,
                                     args=(cmd_arg,)).start()
                elif cmd == prefix + 'ssl':
                    self.do_show_search_list()


            if _user.user_level < 6:

                if cmd == prefix + 'help':
                    self.do_help()
                    
                elif cmd == prefix + 'whatsong':
                    self.do_now_playing()
                elif cmd == prefix + 'status':
                    self.do_playlist_status()
                elif cmd == prefix + 'now':
                    self.do_now_playing()
                elif cmd == prefix + 'whoplayed':
                    self.do_who_plays()
                elif cmd == prefix + 'urb':
                    threading.Thread(
                        target=self.do_search_urban_dictionary, args=(cmd_arg,)).start()
                elif cmd == prefix + 'porn':
                    threading.Thread(
                        target=self.do_porn_search, args=(cmd_arg,)).start()
                elif cmd == prefix + 'wea':
                    threading.Thread(
                        target=self.do_weather_search, args=(cmd_arg,)).start()
                elif cmd == prefix + 'chuck':
                    threading.Thread(target=self.do_chuck_noris).start()
                elif cmd == prefix + '8ball':
                    self.do_8ball(cmd_arg)
                elif cmd == prefix + 'roll':
                    self.do_dice()
                elif cmd == prefix + 'flip':
                    self.do_flip_coin()
                elif cmd == prefix + 'tokes':
                    self.tokesession(cmd_arg)
                elif cmd == prefix + 'cheers':
                    self.tokesession(cmd_arg)
                elif cmd == prefix + 'join':
                    self.tokesession(cmd_arg)
            self.console_write(
                pinylib.COLOR['yellow'], self.active_user.nick + ': ' + cmd + ' ' + cmd_arg)

        else:
            self.console_write(
                pinylib.COLOR['green'], self.active_user.nick + ': ' + msg)

            if self.active_user.user_level > 4:
                threading.Thread(target=self.check_msg, args=(msg,)).start()

        self.active_user.last_msg = msg

    def do_make_mod(self, account):
        """
        Make a tinychat account a room moderator.

        :param account: The account to make a moderator.
        :type account: str
        """
        if self.is_client_owner:
            if len(account) is 0:
                self.send_chat_msg('Missing account name.')
            else:
                tc_user = self.privacy_.make_moderator(account)
                if tc_user is None:
                    self.send_chat_msg('The account is invalid.')
                elif not tc_user:
                    self.send_chat_msg('%s is already a moderator.' % account)
                elif tc_user:
                    self.send_chat_msg(
                        '%s was made a room moderator.' % account)

    def do_remove_mod(self, account):
        """
        Removes a tinychat account from the moderator list.

        :param account: The account to remove from the moderator list.
        :type account: str
        """
        if self.is_client_owner:
            if len(account) is 0:
                self.send_chat_msg('Missing account name.')
            else:
                tc_user = self.privacy_.remove_moderator(account)
                if tc_user:
                    self.send_chat_msg(
                        '%s is no longer a room moderator.' % account)
                elif not tc_user:
                    self.send_chat_msg('%s is not a room moderator.' % account)

    def do_directory(self):
        """ Toggles if the room should be shown on the directory. """
        if self.is_client_owner:
            if self.privacy_.show_on_directory():
                self.send_chat_msg('Room IS shown on the directory.')
            else:
                self.send_chat_msg('Room is NOT shown on the directory.')

    def do_push2talk(self):
        """ Toggles if the room should be in push2talk mode. """
        if self.is_client_owner:
            if self.privacy_.set_push2talk():
                self.send_chat_msg('Push2Talk is enabled.')
            else:
                self.send_chat_msg('Push2Talk is disabled.')

    def do_green_room(self):
        """ Toggles if the room should be in greenroom mode. """
        if self.is_client_owner:
            if self.privacy_.set_greenroom():
                self.send_chat_msg('Green room is enabled.')
            else:
                self.send_chat_msg('Green room is disabled.')

    def do_clear_room_bans_two(self):
        """ Clear all room bans. """
        if self.is_client_owner:
            if self.privacy_.clear_bans():
                self.send_chat_msg('All room bans were cleared.')

    def do_kill(self):
        """ Kills the bot. """
        self.disconnect()

    def do_reboot(self):
        """ Reboots the bot. """
        self.reconnect()

    def do_media_info(self):
        """ Show information about the currently playing youtube. """
        if self.is_client_mod and self.playlist.has_active_track:
            self.send_chat_msg(
                'Playlist Tracks: ' + str(len(self.playlist.track_list)) + '\n' +
                'Track Title: ' + self.playlist.track.title + '\n' +
                'Track Index: ' + str(self.playlist.track_index) + '\n' +
                'Elapsed Track Time: ' + self.format_time(self.playlist.elapsed) + '\n' +
                'Remaining Track Time: ' +
                self.format_time(self.playlist.remaining)
            )

    def do_op_user(self, user_name):

        if self.is_client_mod:
            if len(user_name) is 0:
                self.send_chat_msg('Account can\'t be blank.')
            elif len(user_name) < 3:
                self.send_chat_msg('Account too short: ' +
                                   str(len(user_name)))
            elif self.user_check(user_name) == 4:
                self.send_chat_msg('%s already has the power of BRUH.' % user_name)
            else:
                db = pickledb.load(userdb, False)
                
                user = {'level': 4, 'by': self.active_user.account,
                        'created': time.time()}
                db.dadd('users', (user_name, user))
                db.dump()
             

                self.console_write(pinylib.COLOR['cyan'], '[User] New account %s, BRUH\'d by %s' % (
                    user_name, self.active_user.account))

                self.send_chat_msg('%s has gained BRUH powers!' % user_name)
                
    def do_deop_user(self, user_name):
        """ 
        Lets the room owner, a mod or a bot controller remove a user from being a bot controller.

        :param user_name: The user to deop.
        :type user_name: str
        """
        if self.is_client_mod:
            if len(user_name) is 0:
                self.send_chat_msg('Account can\'t be blank.')
            elif len(user_name) < 3:
                self.send_chat_msg('Account too short: ' +
                                   str(len(user_name)))
            elif self.user_check(user_name) == 5:
                self.send_chat_msg('%s does not have BRUH powers.' % user_name)
            else:
                db = pickledb.load(userdb, False)
                
                user = {'level': 5, 'by': self.active_user.account,
                        'created': time.time()}
                db.dadd('users', (user_name, user))
                db.dump()
             

                self.console_write(pinylib.COLOR['cyan'], '[User] New account %s, de-BRUH\'d by %s' % (
                    user_name, self.active_user.account))

                self.send_chat_msg('%s lost all BRUH powers.' % user_name)

    def do_guests(self):
        """ Toggles if guests are allowed to join the room or not. """
        pinylib.CONFIG.B_ALLOW_GUESTS = not pinylib.CONFIG.B_ALLOW_GUESTS
        self.send_chat_msg('Allow Guests: %s' % pinylib.CONFIG.B_ALLOW_GUESTS)

    def do_greet(self):
        """ Toggles if users should be greeted on entry. """
        pinylib.CONFIG.B_GREET = not pinylib.CONFIG.B_GREET
        self.send_chat_msg('Greet Users: %s' % pinylib.CONFIG.B_GREET)

    def do_kick_as_ban(self):
        """ Toggles if kick should be used instead of ban for auto bans . """
        pinylib.CONFIG.B_USE_KICK_AS_AUTOBAN = not pinylib.CONFIG.B_USE_KICK_AS_AUTOBAN
        self.send_chat_msg('Use Kick As Auto Ban: %s' %
                           pinylib.CONFIG.B_USE_KICK_AS_AUTOBAN)

    def do_youtube_playlist_search(self, search_str):
        """
        Search youtube for a playlist.

        :param search_str: The search term to search for.
        :type search_str: str
        """
        if self.is_client_mod:
            if len(search_str) == 0:
                self.send_chat_msg('Missing search string.')
            else:
                self.search_list = youtube.playlist_search(search_str)
                if len(self.search_list) > 0:
                    self.is_search_list_yt_playlist = True
                    _ = '\n'.join('(%s) %s' % (
                        i, d['playlist_title']) for i, d in enumerate(self.search_list))
                    self.send_chat_msg(_)
                else:
                    self.send_chat_msg(
                        'Failed to find playlist matching search term: %s' % search_str)

    def do_play_youtube_playlist(self, int_choice):
        """
        Play a previous searched playlist.

        :param int_choice: The index of the playlist.
        :type int_choice: str | int
        """
        if self.is_client_mod:
            if self.is_search_list_yt_playlist:
                try:
                    int_choice = int(int_choice)
                except ValueError:
                    self.send_chat_msg('Only numbers allowed.')
                else:
                    if 0 <= int_choice <= len(self.search_list) - 1:
                        self.send_chat_msg(
                            'Please wait while creating playlist..')
                        tracks = youtube.playlist_videos(
                            self.search_list[int_choice])
                        if len(tracks) > 0:
                            self.playlist.add_list(
                                self.active_user.nick, tracks)
                            self.send_chat_msg(
                                '🎶 Added %s tracks from youtube playlist.' % len(tracks))
                            if not self.playlist.has_active_track:
                                track = self.playlist.next_track
                                self.send_yut_play(
                                    track.id, track.time, track.title)
                                self.timer(track.time)
                        else:
                            self.send_chat_msg(
                                'Failed to retrieve videos from youtube playlist.')
                    else:
                        self.send_chat_msg(
                            'Please make a choice between 0-%s' % str(len(self.search_list) - 1))
            else:
                self.send_chat_msg(
                    'The search list does not contain any youtube playlist id\'s.')

    def do_show_search_list(self):
        """ Show what the search list contains. """
        if self.is_client_mod:
            if len(self.search_list) == 0:
                self.send_chat_msg('The search list is empty.')
            elif self.is_search_list_yt_playlist:
                _ = '\n'.join('(%s) - %s' % (i, d['playlist_title'])
                              for i, d in enumerate(self.search_list))
                self.send_chat_msg('Youtube Playlist\'s\n' + _)
            else:
                _ = '\n'.join('(%s) %s %s' % (i, d['video_title'], self.format_time(d['video_time']))
                              for i, d in enumerate(self.search_list))
                self.send_chat_msg('🎶 Youtube Tracks\n' + _)

    def do_skip(self):
        """ Skip to the next item in the playlist. """
        if self.is_client_mod:
            if self.playlist.is_last_track is None:
                self.send_chat_msg('No tune next. The playlist is empty. !stop to clear current track.')
            elif self.playlist.is_last_track:
                self.send_chat_msg('This is the last track in the playlist.')
            else:
                self.cancel_timer()
                next_track = self.playlist.next_track
                self.send_yut_play(
                    next_track.id, next_track.time, next_track.title)
                self.timer(next_track.time)

    # TODO: Make sure this is working.
    def do_delete_playlist_item(self, to_delete):
        """
        Delete items from the playlist.

        :param to_delete: Item indexes to delete.
        :type to_delete: str
        """
        if self.is_client_mod:
            if len(self.playlist.track_list) == 0:
                self.send_chat_msg('The playlist is empty.')
            elif len(to_delete) == 0:
                self.send_chat_msg('No indexes provided.')
            else:
                indexes = None
                by_range = False

                try:
                    if ':' in to_delete:
                        range_indexes = map(int, to_delete.split(':'))
                        temp_indexes = range(
                            range_indexes[0], range_indexes[1] + 1)
                        if len(temp_indexes) > 1:
                            by_range = True
                    else:
                        temp_indexes = map(int, to_delete.split(','))
                except ValueError as ve:
                    log.error('wrong format: %s' % ve)
                else:
                    indexes = []
                    for i in temp_indexes:
                        if i < len(self.playlist.track_list) and i not in indexes:
                            indexes.append(i)

                if indexes is not None and len(indexes) > 0:
                    result = self.playlist.delete(indexes, by_range)
                    if result is not None:
                        if by_range:
                            self.send_chat_msg('Deleted from index: %s to index: %s' %
                                               (result['from'], result['to']))
                        elif result['deleted_indexes_len'] is 1:
                            self.send_chat_msg('Deleted %s' %
                                               result['track_title'])
                        else:
                            self.send_chat_msg('Deleted tracks at index: %s' %
                                               ', '.join(result['deleted_indexes']))
                    else:

                        self.send_chat_msg('Nothing was deleted.')

    def do_create_password(self):
        global _KEYWORDS
        word = random.choice(_KEYWORDS)
        numbers = str(randint(100, 999))
        xpassword = word + numbers

        return xpassword

    def do_media_replay(self):
        """ Replay the currently playing track. """
        if self.is_client_mod:
            if self.playlist.track is not None:
                self.cancel_timer()
                track = self.playlist.replay()
                self.send_yut_play(track.id, track.time, track.title)
                self.timer(track.time)

    def do_play_media(self):
        """ Play a track on pause . """
        if self.is_client_mod:
            if self.playlist.track is not None:
                if self.playlist.has_active_track:
                    self.cancel_timer()
                if self.playlist.is_paused:
                    self.playlist.play(self.playlist.elapsed)
                    self.send_yut_play(self.playlist.track.id, self.playlist.track.time,
                                       self.playlist.track.title, self.playlist.elapsed)  #
                    self.timer(self.playlist.remaining)

    def do_media_pause(self):
        """ Pause a track. """
        if self.is_client_mod:
            track = self.playlist.track
            if track is not None:
                if self.playlist.has_active_track:
                    self.cancel_timer()
                self.playlist.pause()
                self.send_yut_pause(track.id, track.time,
                                    self.playlist.elapsed)

    def do_close_media(self):
        """ Close a track playing. """
        if self.is_client_mod:
            if self.playlist.has_active_track:
                self.cancel_timer()
                self.playlist.stop()
                self.send_yut_stop(
                    self.playlist.track.id, self.playlist.track.time, self.playlist.elapsed)

    def do_seek_media(self, time_point):
        """
        Time search a track.

        :param time_point: The time point in which to search to.
        :type time_point: str
        """
        if self.is_client_mod:
            if ('h' in time_point) or ('m' in time_point) or ('s' in time_point):
                offset = pinylib.string_util.convert_to_seconds(time_point)
                if offset == 0:
                    self.send_chat_msg('Invalid seek time.')
                else:
                    track = self.playlist.track
                    if track is not None:
                        if 0 < offset < track.time:
                            if self.playlist.has_active_track:
                                self.cancel_timer()
                            if self.playlist.is_paused:
                                self.playlist.pause(offset=offset)  #
                                self.send_yut_pause(
                                    track.id, track.time, offset)
                            else:
                                self.playlist.play(offset)
                                self.send_yut_play(
                                    track.id, track.time, track.title, offset)
                                self.timer(self.playlist.remaining)

    def do_clear_playlist(self):
        """ Clear the playlist for items."""
        if self.is_client_mod:
            if len(self.playlist.track_list) > 0:
                pl_length = str(len(self.playlist.track_list))
                self.playlist.clear()
                self.send_chat_msg(
                    'Deleted %s items in the playlist.' % pl_length)
            else:
                self.send_chat_msg('The playlist is empty, nothing to delete.')

    def do_playlist_info(self):  # TODO: this needs more work !
        """ Shows the next tracks in the playlist. """
        if self.is_client_mod:
            if len(self.playlist.track_list) > 0:
                tracks = self.playlist.get_tracks()
                if len(tracks) > 0:
                    # If i is 0 then mark that as the next track
                    _ = '\n'.join('(%s) - %s %s' % (track[0], track[1].title, self.format_time(track[1].time))
                                  for i, track in enumerate(tracks))
                    self.send_chat_msg(_)

    def do_youtube_search(self, search_str):
        """ 
        Search youtube for a list of matching candidates.

        :param search_str: The search term to search for.
        :type search_str: str
        """
        if self.is_client_mod:
            if len(search_str) == 0:
                self.send_chat_msg('Missing search string.')
            else:
                self.search_list = youtube.search_list(search_str, results=5)
                if len(self.search_list) > 0:
                    self.is_search_list_yt_playlist = False
                    _ = '\n'.join('(%s) %s %s' % (i, d['video_title'], self.format_time(d['video_time']))
                                  for i, d in enumerate(self.search_list))  #
                    self.send_chat_msg(_)
                else:
                    self.send_chat_msg(
                        'Could not find anything matching: %s' % search_str)

    def do_play_youtube_search(self, int_choice):
        """
        Play a track from a previous youtube search list.

        :param int_choice: The index of the track in the search.
        :type int_choice: str | int
        """
        if self.is_client_mod:
            if not self.is_search_list_yt_playlist:
                if len(self.search_list) > 0:
                    try:
                        int_choice = int(int_choice)
                    except ValueError:
                        self.send_chat_msg('Only numbers allowed.')
                    else:
                        if 0 <= int_choice <= len(self.search_list) - 1:

                            if self.playlist.has_active_track:
                                track = self.playlist.add(
                                    self.active_user.nick, self.search_list[int_choice])
                                self.send_chat_msg('Added (%s) %s %s' %
                                                   (self.playlist.last_index,
                                                    track.title, self.format_time(track.time)))
                            else:
                                track = self.playlist.start(
                                    self.active_user.nick, self.search_list[int_choice])
                                self.send_yut_play(
                                    track.id, track.time, track.title)
                                self.timer(track.time)
                        else:
                            self.send_chat_msg(
                                'Please make a choice between 0-%s' % str(len(self.search_list) - 1))
                else:
                    self.send_chat_msg(
                        'No youtube track id\'s in the search list.')
            else:
                self.send_chat_msg(
                    'The search list only contains youtube playlist id\'s.')

    def do_clear(self):
        """ Clears the chat box. """
        self.send_chat_msg('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
                           '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

    def do_kick(self, user_name):
        """ 
        Kick a user out of the room.

        :param user_name: The username to kick.
        :type user_name: str
        """
        if self.is_client_mod:
            if len(user_name) is 0:
                self.send_chat_msg('Missing username.')
            elif user_name == self.nickname:
                self.send_chat_msg('Action not allowed.')
            else:
                if user_name.startswith('*'):
                    user_name = user_name.replace('*', '')
                    _users = self.users.search_containing(user_name)
                    if len(_users) > 0:
                        for i, user in enumerate(_users):
                            if user.nick != self.nickname and user.user_level > self.active_user.user_level:
                                if i <= pinylib.CONFIG.B_MAX_MATCH_BANS - 1:
                                    self.send_kick_msg(user.id)
                else:
                    _user = self.users.search_by_nick(user_name)
                    if _user is None:
                        self.send_chat_msg('No user named: %s' % user_name)
                    elif _user.user_level < self.active_user.user_level:
                        self.send_chat_msg(
                            'imma let ya guys figure that out...')
                    else:
                        self.send_kick_msg(_user.id)

    def do_forgive(self, nick_name):
        """
        Forgive a user based on if their user id (uid) is found in the room's ban list.
        :param nick_name: str the nick name of the user that was banned.
        """
        global banlist
        forgiven = False

        if self.is_client_mod:
            if len(nick_name) is 0:
                self.send_chat_msg(
                    ' Please state a nick to forgive from the ban list.')
            else:
                for item in banlist['items']:
                    if item['nick'] == nick_name:
                        self.users.delete_banned_user(item)
                        self.send_unban_msg(item['id'])
                        forgiven = True
                    else:
                        self.send_chat_msg(
                            nick_name + ' was not found in the banlist')
                if forgiven:
                    self.send_chat_msg(nick_name + ' was forgiven.')

    def on_banlist(self, banlist_info):
        """
        Return json from servers 
        """

        global banlist
        banlist = banlist_info

    def do_ban(self, user_name):
        """ 
        Ban a user from the room.

        :param user_name: The username to ban.
        :type user_name: str
        """
        if self.is_client_mod:
            if len(user_name) is 0:
                self.send_chat_msg('Missing username.')
            elif user_name == self.nickname:
                self.send_chat_msg('Action not allowed.')
            else:
                if user_name.startswith('*'):
                    user_name = user_name.replace('*', '')
                    _users = self.users.search_containing(user_name)
                    if len(_users) > 0:
                        for i, user in enumerate(_users):
                            if user.nick != self.nickname and user.user_level > self.active_user.user_level:
                                if i <= pinylib.CONFIG.B_MAX_MATCH_BANS - 1:
                                    self.send_ban_msg(user.id)
                else:
                    _user = self.users.search_by_nick(user_name)
                    if _user is None:
                        self.send_chat_msg('No user named: %s' % user_name)
                    elif _user.user_level < self.active_user.user_level:
                        self.send_chat_msg(
                            'i dont wanna be a part of ya problems..')
                    else:
                        self.send_ban_msg(_user.id)

    def do_bad_nick(self, bad_nick):
        """ 
        Adds a username to the nick bans file.

        :param bad_nick: The bad nick to write to the nick bans file.
        :type bad_nick: str
        """
        if self.is_client_mod:
            if len(bad_nick) is 0:
                self.send_chat_msg('Missing username.')
            elif self.nick_check(bad_nick):
                self.send_chat_msg('%s is already in list.' % bad_nick)
            else:
                db = pickledb.load(userdb, False)
                user = {'by': self.active_user.account,
                        'created': time.time(), 'reason': 'NA'}
                db.dadd('badnicks', (bad_nick, user))
                db.dump()
          

                self.send_chat_msg('%s was added to banned nicks.' % bad_nick)

    def do_remove_bad_nick(self, bad_nick):
        """ 
        Removes nick from the nick bans file.

        :param bad_nick: The bad nick to remove from the nick bans file.
        :type bad_nick: str
        """
        if self.is_client_mod:
            if len(bad_nick) is 0:
                self.send_chat_msg('Missing username')
            else:
                if not self.nick_check(bad_nick):
                    self.send_chat_msg(
                        '%s is not in the banned nicks.' % bad_nick)
                else:
                    db = pickledb.load(userdb, False)
                    db.dpop('badnicks', bad_nick)
                    db.dump()
                   
                    self.send_chat_msg(
                        '%s removed from banned nicks.' % bad_nick)

    def do_bad_string(self, bad_string):
        """ 
        Adds a string to the string bans file.

        :param bad_string: The bad string to add to the string bans file.
        :type bad_string: str
        """
        if self.is_client_mod:
            if len(bad_string) is 0:
                self.send_chat_msg('Ban string can\'t be blank.')
            elif len(bad_string) < 3:
                self.send_chat_msg(
                    'Ban string to short: ' + str(len(bad_string)))
            elif self.word_check(bad_string):
                self.send_chat_msg('%s is already in list.' % bad_string)
            else:
                db = pickledb.load(userdb, False)
                user = {'by': self.active_user.account,
                        'created': time.time(), 'reason': 'NA'}
                db.dadd('badwords', (bad_string, user))
                db.dump()
           
                self.send_chat_msg(
                    '%s was added to banned words.' % bad_string)

    def do_remove_bad_string(self, bad_string):
        """ 
        Removes a string from the string bans file.

        :param bad_string: The bad string to remove from the string bans file.
        :type bad_string: str
        """
        if self.is_client_mod:
            if len(bad_string) is 0:
                self.send_chat_msg('Missing word string.')
            else:

                if not self.word_check(bad_string):
                    self.send_chat_msg('%s is not banned.' % bad_string)

                else:
                    db = pickledb.load(userdb, False)
                    db.dpop('badwords', bad_string)
                    db.dump()

                    self.send_chat_msg(
                        '%s was removed to banned words.' % bad_string)

    def do_bad_account(self, bad_account_name):
        """ 
        Adds an account name to the account bans file.

        :param bad_account_name: The bad account name to add to the account bans file.
        :type bad_account_name: str
        """

        if self.is_client_mod:
            if len(bad_account_name) is 0:
                self.send_chat_msg('Account can\'t be blank.')
            elif len(bad_account_name) < 3:
                self.send_chat_msg('Account to short: ' +
                                   str(len(bad_account_name)))
            elif self.user_check(bad_account_name) == 9:
                self.send_chat_msg('%s is already in list.' % bad_account_name)
            else:

                db = pickledb.load(userdb, False)
                if self.user_check(bad_account_name) > 0:
                    db.dpop('users', bad_account_name)


                user = {'level': 9, 'by': self.active_user.account,
                        'created': time.time(), 'reason': 'NA'}
                db.dadd('users', (bad_account_name, user))
                db.dump()
           

                self.send_chat_msg(
                    '%s was added to banned accounts.' % bad_account_name)

    def do_remove_bad_account(self, bad_account):
        """ 
        Removes an account from the account bans file.

        :param bad_account: The badd account name to remove from account bans file.
        :type bad_account: str
        """
        if self.is_client_mod:
            if len(bad_account) is 0:
                self.send_chat_msg('Missing account.')
            else:
                if self.user_check(bad_account) == 9:
                    db = pickledb.load(userdb, False)
                    db.dpop('users', bad_account)
                    db.dump()
                 
                    self.send_chat_msg(
                        '%s is not in banned accounts.' % bad_account)

    def do_verified(self, verified_name):

        if self.is_client_mod:
            if len(verified_name) is 0:
                self.send_chat_msg('Account can\'t be blank.')
            elif len(verified_name) < 3:
                self.send_chat_msg('Account too short: ' +
                                   str(len(verified_name)))
            elif self.user_check(verified_name) == 5:
                self.send_chat_msg('%s already has yt powers.' % verified_name)
            else:
                db = pickledb.load(userdb, False)
                
                user = {'level': 5, 'by': self.active_user.account,
                        'created': time.time()}
                db.dadd('users', (verified_name, user))
                db.dump()
             

                self.console_write(pinylib.COLOR['cyan'], '[User] New account %s, verified by %s' % (
                    verified_name, self.active_user.account))

                self.send_chat_msg('%s now has yt powers!' % verified_name)
                
    
    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::HUNTING:::::::::::::::::::::::::::::::::::::::::::::::::::::
    """
    def do_hunt(self):
        prefix = pinylib.CONFIG.B_PREFIX
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)
        has_weapon = self.weapon_level_check(_user.account)
        hunt_trip = 0
        
        if has_weapon != 0:
            if hunt_trip == "cancel":
                if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                    self.resethunt()
                    self.send_chat_msg('hunt trip has been abandoned!')
                return
            hunt_trip = "3"
            if self.hunt_mode:
                mins = self.until(self.hunt_start, self.hunt_end)

                if self.active_user.nick in self.hunters:
                        self.send_chat_msg(
                            '✋ You\'re already on the hunting trip! \n %s %s left until we return...' % (str(mins), self.pluralize('min', mins)))
                elif len(self.hunters) == 3:
                        self.send_chat_msg(
                            '✋ Hunting Trip is Full! \n %s %s left until they return...' % (str(mins), self.pluralize('min', mins)))
                else:
                    self.newhunter()
                
                return
            else:
                if self.active_user.user_level < 6:
                    try:
                        end = int(hunt_trip)
                        if not 1 <= end <= 10:
                            raise Exception()
                    except:
                        self.send_chat_msg('hunt BITCHES')
                        return

                    announce = 1
                    self.hunters.append(self.active_user.nick)
                    self.starthunt(end, announce)
                    mins = self.until(self.hunt_start, self.hunt_end)
                    self.send_chat_msg(
                        '🦌 3-Man Hunting Trip! \n -- %s %s until the hunt ends! \n -- Type %shunt to join!' % (
                            str(mins), self.pluralize('min', mins), prefix))
        else:
            self.send_chat_msg(
                'A weapon is required. !shop')

    def newhunter(self):
        joinicon = ['🦌']
        self.hunters.append(self.active_user.nick);
        mins = self.until(self.hunt_start, self.hunt_end)
        time.sleep(0.9)
        self.send_chat_msg('%s %s has joined the hunt!' % (
            random.choice(joinicon), self.active_user.nick))
        return
        
    def starthunt(self, end, hannounce=0):
        self.hunt_mode = True
        ht = int(time.time())
        self.hannounce = int(hannounce) * 60
        self.hannounceCheck = ht + self.hannounce
        self.hunt_start = ht
        self.hunt_end = int(end) * 60
        thread = threading.Thread(target=self.hunt_count, args=())
        thread.daemon = True
        thread.start()

    def resethunt(self):
        self.hunt_mode = False
        self.hannounce = 0
        self.hannounceCheck = 0
        self.hunters[:] = []
        self.hunt_start = 0
        self.hunter = None
        self.hunted[:] = []
        return

    def hunt_count(self):
        _user = self.users.search_by_nick(self.active_user.nick)
        gamer_name = _user.account
        coins = self.bc_check(_user.account)
        self.hunted[:] = []
        
        prefix = pinylib.CONFIG.B_PREFIX
        while True:
            time.sleep(0.3)
            ht = time.time()

            if not self.hunt_mode:
                time.sleep(5)
                break

            if self.hunter is None:
                self.hunter = str(self.hunters[0])

            if ht > self.hunt_start + self.hunt_end:
                start = int((ht - self.hunt_start) / 60)

                if len(self.hunters) > 1:
                    if len(self.hunters) == 2:
                        joined = self.hunters[1]
                    else:
                        joined = ''
                        j = 0
                        for name in self.hunters[1:]:
                            if j == len(self.hunters) - 2:
                                joined += 'and ' + name
                            else:
                                joined += name + ', '
                            j += 1

                    fuckinggrammar = 'is'
                    if len(self.hunters) > 2:
                        fuckinggrammar = 'are'

                for u in self.hunters:
                    _user = self.users.search_by_nick(u)
                    gamer_name = _user.account
                    coins = self.bc_check(_user.account)
                    weapon_damage = self.weapon_damage_check(_user.account)
                    weapon_class = self.weapon_class_check(_user.account)
                    has_weapon = self.weapon_level_check(_user.account)
                    
                    db = pickledb.load(userdb, False)
                    time.sleep(1)
                    h_type = ['👾 ALIENs','🤖 ROBOTs','👺 GOBLINs','👹 OGREs','👻 ENDER MEN']
                    hunt_type = random.choice(h_type)
                    
                    h_size = ['3','4','5']
                    hunt_size = random.choice(h_size)
                    
                    h_divider = ['8','9','10','11','12','13','14','15','16','17','18','19','20']
                    hunt_divider = random.choice(h_divider)
                    
                    if weapon_class == 'bow':
                        r_bonus = ['0','50',]
                        range_bonus = random.choice(r_bonus)
                    elif weapon_class != 'bow':
                        range_bonus = '0'
                    
                    damage_1 = (int(weapon_damage)*int(hunt_size))
                    damage_2 = (int(damage_1)+int(range_bonus))
                    damage_2a = (int(damage_2)/int(hunt_divider))
                    damage_3 = int(round(damage_2a, 1))

                    f_sum = damage_3 + coins
                    user = {'bruhcoins': f_sum,
                            'lastcoin': time.time()}
                    db.dadd('gamers', (gamer_name, user))
                    db.dump()                 

                    self.console_write(pinylib.COLOR['cyan'], '[User] New Hunter : %s : %s : %s' % (
                        gamer_name, damage_2, damage_3))
                    _level = self.user_check(_user.account)
                    if damage_2 == 0:
                        self.hunted.append('%s fought nothing!' % (u))
                    else: 
                        self.hunted.append('%s fought %s %s! \n Looting 💰%s along the way! \n' % (u, hunt_size, hunt_type, damage_3))

                full_hunted = '\n'.join(self.hunted)
                self.send_chat_msg('%s' % (full_hunted))
                self.resethunt()
                
                break

            if ht > self.hannounceCheck:
                self.hannounceCheck = ht + self.hannounce

                start = int((ht - self.hunt_start) / 60)  
   
    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::FISHING:::::::::::::::::::::::::::::::::::::::::::::::::::::
    """
    def do_fish(self):

        prefix = pinylib.CONFIG.B_PREFIX
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)
        fish_trip = 0
        
        if fish_trip == "cancel":
            if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                self.resetfish()
                self.send_chat_msg('fish trip has been abandoned!')
            return
        fish_trip = "1"
        if self.fish_mode:
            mins = self.until(self.fish_start, self.fish_end)

            if self.active_user.nick in self.fishers:
                self.send_chat_msg(
                    '✋ You\'re already on the fishing trip! \n ⛵ %s %s left until we return...' % (str(mins), self.pluralize('min', mins)))
            else:
                self.newfisher()
            return
        else:
            if self.active_user.user_level < 6:
                try:
                    end = int(fish_trip)
                    if not 1 <= end <= 10:
                        raise Exception()
                except:
                    self.send_chat_msg('FISH BITCHES')
                    return

                announce = 1
                self.fishers.append(self.active_user.nick)
                self.startFish(end, announce)
                mins = self.until(self.fish_start, self.fish_end)
                self.send_chat_msg(
                    'Chartering a fishing trip! \n ⛵ %s %s until the fishing boat leaves! \n Type %sfish to join the trip!' % (
                        str(mins), self.pluralize('min', mins), prefix))

    def newfisher(self):
        joinicon = ['🎣']
        self.fishers.append(self.active_user.nick)
        mins = self.until(self.fish_start, self.fish_end)
        time.sleep(0.9)
        self.send_chat_msg('%s %s has joined the fishing trip!' % (
            random.choice(joinicon), self.active_user.nick))
        return
        
    def startFish(self, end, fannounce=0):
        self.fish_mode = True
        ft = int(time.time())
        self.fannounce = int(fannounce) * 60
        self.fannounceCheck = ft + self.fannounce
        self.fish_start = ft
        self.fish_end = int(end) * 60
        thread = threading.Thread(target=self.fish_count, args=())
        thread.daemon = True
        thread.start()

    def resetfish(self):
        self.fish_mode = False
        self.fannounce = 0
        self.fannounceCheck = 0
        self.fishers[:] = []
        self.fish_start = 0
        self.fisher = None
        self.catch[:] = []
        return

    def fish_count(self):
        _user = self.users.search_by_nick(self.active_user.nick)
        gamer_name = _user.account
        coins = self.bc_check(_user.account)
        self.catch[:] = []
        
        prefix = pinylib.CONFIG.B_PREFIX
        while True:
            time.sleep(0.3)
            ft = time.time()

            if not self.fish_mode:
                time.sleep(5)
                break

            if self.fisher is None:
                self.fisher = str(self.fishers[0])

            if ft > self.fish_start + self.fish_end:
                start = int((ft - self.fish_start) / 60)

                if len(self.fishers) > 1:
                    if len(self.fishers) == 2:
                        joined = self.fishers[1]
                    else:
                        joined = ''
                        j = 0
                        for name in self.fishers[1:]:
                            if j == len(self.fishers) - 2:
                                joined += 'and ' + name
                            else:
                                joined += name + ', '
                            j += 1

                    fuckinggrammar = 'is'
                    if len(self.fishers) > 2:
                        fuckinggrammar = 'are'

                for u in self.fishers:
                    _user = self.users.search_by_nick(u)
                    gamer_name = _user.account
                    coins = self.bc_check(_user.account)
                    pole_level = self.pole_level_check(_user.account)
                    
                    db = pickledb.load(userdb, False)
                    time.sleep(1)
                    fish_type = ['🐟 Fish','🐡 Blowfish','🐠 Tropical','🐙 Octopus','🦈 Shark']
                    fish_size = ['1','2','3','4','5','6','7','8','9','10','0','0','0','0','40']
                    if pole_level == 1:
                        fish_size = ['5','6','7','8','9','10','0','0','0','0','50']
                    elif pole_level == 2:
                        fish_size = ['7','8','9','10','11','12','0','0','0','50']
                    elif pole_level == 3:
                        fish_size = ['10','11','12','13','14','15','10','10','10','10','1','1','75','75']                  

                    f_type = random.choice(fish_type)
                    f_size = int(random.choice(fish_size))

                    f_sum = f_size + coins
                    user = {'bruhcoins': f_sum,
                            'lastcoin': time.time()}
                    db.dadd('gamers', (gamer_name, user))
                    db.dump()
                 

                    self.console_write(pinylib.COLOR['cyan'], '[User] New Fisher : %s : %s : %s' % (
                        gamer_name, f_type, f_size))
                    _level = self.user_check(_user.account)
                    if f_size == 0:
                        self.catch.append('%s caught nothing! \n ' % (u))
                    else: 
                        self.catch.append('%s caught a %s lb %s! \n ' % (u, f_size, f_type))

                full_catch = '\n'.join(self.catch)
                self.send_chat_msg('%s' % (full_catch))
                self.resetfish()
                
                break

            if ft > self.fannounceCheck:
                self.fannounceCheck = ft + self.fannounce

                start = int((ft - self.fish_start) / 60)
                
    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::FISHING:POLES:::::::::::::::::::::::::::::::::::::::::::::::::
    """ 
    def buy_pole(self, choice):
       
        if self.is_client_mod:
            _user = self.users.search_by_nick(self.active_user.nick)
            _level = self.user_check(_user.account)
            item_category = 'pole' 
            data_base = 'fishing_poles'
            buy_level = 'pole_level'
            buy_type = 'pole_type'
            buy_changed = 'pole_changed'
            buy_damage = 'pole_damage'
            
            if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                try:
                    end = int(choice)
                    if not 1 <= end <= 10:
                        raise Exception()
                except:
                    self.send_chat_msg('Please use !%s <#> when buying a %s.' % (item_category, item_category))
                    return
                    
                _user = self.users.search_by_nick(self.active_user.nick)
                choice = int(choice)
                gamer_name = _user.account
                coins = self.bc_check(_user.account)

                current_level = self.pole_level_check(_user.account)
                
                if self.is_client_mod:
                    if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                        if choice == 1:
                        
                            item_level = 1
                            item_price = 750
                            item_type = 'Wooden'
                            item_damage = 0
                            
                            if current_level >= item_level:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_level))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 2:
                        
                            item_level = 2
                            item_price = 1500
                            item_type = 'Steel'
                            item_damage = 0
                            
                            if current_level >= item_level:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_level))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                

                        elif choice == 3:
                        
                            item_level = 3
                            item_price = 10000
                            item_type = 'Bamboo'
                            item_damage = 0
                            
                            if current_level >= item_level:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_level))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                        

    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::STORE:::::::::::::::::::::::::::::::::::::::::::::::::::::
    """ 
    def open_shop(self):
       
        if self.is_client_mod:
                time.sleep(1)
                self.send_chat_msg(' 🛒 BRUH SHOP 🛍️ \n ----------------------------------------- \n 🎣 !pole_shop \n ⚔️ !sword_shop \n 🏹 !bow_shop \n \n Note: You are only allowed 1 weapon.')
                
    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::STORES:::::::::::::::::::::::::::::::::::::::::::::::::::::
    """ 
    def open_shop_poles(self):
       
        if self.is_client_mod:
                time.sleep(1)
                self.send_chat_msg(' 🎣 Fishing Shop 🎏\n ----------------------------------------- \n !pole 1 : Wooden 💰750 \n !pole 2 : Steel 💰1500 \n !pole 3 : Bamboo 💰10,000 \n \n Use !pole <#> to purchase \n Use !pole_stats to see stats')
    def pole_stats(self):
        if self.is_client_mod:
                time.sleep(1)
                self.send_chat_msg(' 🎣 Pole Stats 📊 \n ----------------------------------------- \n 0 | 01-10 lbs | 6% chance of 40 lb \n  1 | 05-10 lbs | 9% chance of 50 lb \n  2 | 07-12 lbs | 10% chance of 50 lb \n  3 | 10-15 lbs | 14% chance of 75 lb')
                
                
    def open_shop_swords(self):
       
        if self.is_client_mod:
                time.sleep(1)
                self.send_chat_msg(' ⚔️ Sword Shop 🛡️ \n ----------------------------------------- \n !sword 1 : Wooden 💰800 \n !sword 2 : Stone 💰1500 \n !sword 3 : Iron 💰2500 \n !sword 4 : Gold 💰4000 \n !sword 5 : Diamond 💰10000 \n \n Use !sword <#> to purchase \n Use !sword_stats to see stats')
    def sword_stats(self):
        if self.is_client_mod:
                time.sleep(1)
                self.send_chat_msg(' ⚔️ Sword Stats 📊 \n ----------------------------------------- \n 0 | 100 Dmg \n  1 | 150 Dmg \n  2 | 250 Dmg \n  3 | 500 Dmg \n  4 | 750 Dmg \n  5 | 1200')
                
    def open_shop_bows(self):
       
        if self.is_client_mod:
                time.sleep(1)
                self.send_chat_msg(' 🏹 Bow Shop 🛡️ \n ----------------------------------------- \n  Range Bonus = 50% chance +50 Dmg \n ----------------------------------------- \n !bow 1 : Wooden 💰800 \n !bow 2 : Stone 💰1500 \n !bow 3 : Iron 💰2500 \n !bow 4 : Gold 💰4000 \n !bow 5 : Diamond 💰10000  \n \n Use !bow <#> to purchase \n Use !bow_stats to see stats')  
    def bow_stats(self):
       
        if self.is_client_mod:
                time.sleep(1)
                self.send_chat_msg(' 🏹 Bow Stats 📊 \n ----------------------------------------- \n 0 | 100 Dmg \n  1 | 125 Dmg \n  2 | 225 Dmg \n  3 | 475 Dmg \n  4 | 725 Dmg \n  5 | 1175 Dmg \n \n Range Bonus = 50% chance +50 Dmg on ALL')            
                
    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::FISHING:POLES:::::::::::::::::::::::::::::::::::::::::::::::::
    """ 
    def buy_sword(self, choice):
       
        if self.is_client_mod:
            _user = self.users.search_by_nick(self.active_user.nick)
            _level = self.user_check(_user.account)
            item_category = 'sword' 
            data_base = 'weapons'
            buy_level = 'weapon_level'
            buy_type = 'weapon_type'
            buy_changed = 'weapon_changed'
            buy_damage = 'weapon_damage'
            buy_category = 'weapon_class'
            
            if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                try:
                    end = int(choice)
                    if not 1 <= end <= 10:
                        raise Exception()
                except:
                    self.send_chat_msg('Please use !%s <#> when buying a %s.' % (item_category, item_category))
                    return
                    
                _user = self.users.search_by_nick(self.active_user.nick)
                choice = int(choice)
                gamer_name = _user.account
                coins = self.bc_check(_user.account)

                current_dmg = self.weapon_damage_check(_user.account)
                
                if self.is_client_mod:
                    if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                        if choice == 1:
                        
                            item_level = 1
                            item_price = 750
                            item_type = 'Wooden'
                            item_damage = 150
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 2:
                        
                            item_level = 2
                            item_price = 1500
                            item_type = 'Stone'
                            item_damage = 250
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 3:
                        
                            item_level = 3
                            item_price = 2500
                            item_type = 'Iron'
                            item_damage = 500
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 4:
                        
                            item_level = 4
                            item_price = 4000
                            item_type = 'Gold'
                            item_damage = 750
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 5:
                        
                            item_level = 5
                            item_price = 10000
                            item_type = 'Diamond'
                            item_damage = 1200
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                                
    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::FISHING:POLES:::::::::::::::::::::::::::::::::::::::::::::::::
    """ 
    def buy_bow(self, choice):
       
        if self.is_client_mod:
            _user = self.users.search_by_nick(self.active_user.nick)
            _level = self.user_check(_user.account)
            item_category = 'bow' 
            data_base = 'weapons'
            buy_level = 'weapon_level'
            buy_type = 'weapon_type'
            buy_changed = 'weapon_changed'
            buy_damage = 'weapon_damage'
            buy_category = 'weapon_class'
            
            if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                try:
                    end = int(choice)
                    if not 1 <= end <= 10:
                        raise Exception()
                except:
                    self.send_chat_msg('Please use !%s <#> when buying a %s.' % (item_category, item_category))
                    return
                    
                _user = self.users.search_by_nick(self.active_user.nick)
                choice = int(choice)
                gamer_name = _user.account
                coins = self.bc_check(_user.account)

                current_dmg = self.weapon_damage_check(_user.account)
                
                if self.is_client_mod:
                    if self.active_user.user_level < 5 or _level == 5 or _level == 4:
                        if choice == 1:
                        
                            item_level = 1
                            item_price = 750
                            item_type = 'Wooden'
                            item_damage = 125
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 2:
                        
                            item_level = 2
                            item_price = 1500
                            item_type = 'Stone'
                            item_damage = 225
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 3:
                        
                            item_level = 3
                            item_price = 2500
                            item_type = 'Iron'
                            item_damage = 475
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 4:
                        
                            item_level = 4
                            item_price = 4000
                            item_type = 'Gold'
                            item_damage = 725
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                                
                        elif choice == 5:
                        
                            item_level = 5
                            item_price = 10000
                            item_type = 'Diamond'
                            item_damage = 1175
                            
                            if current_dmg >= item_damage:
                                self.send_chat_msg('You have the same/better %s!' % (item_category))
                            elif coins == 0:
                                self.send_chat_msg('You\'re Broke!')
                            elif coins < item_price:
                                self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: %s' % (_user.nick, coins))
                            else:
                                db = pickledb.load(userdb, False)
                                
                                user = {buy_level: item_level,
                                        buy_changed: time.time(),
                                        buy_type: item_type,
                                        buy_damage: item_damage,
                                        buy_category: item_category}
                                db.dadd(data_base, (gamer_name, user))
                                db.dump()
                                
                                buy_sum = coins - item_price 
                                user = {'bruhcoins': buy_sum,
                                        'lastcoin': time.time()}
                                db.dadd('gamers', (gamer_name, user))
                                db.dump()

                                self.console_write(pinylib.COLOR['cyan'], '[User] New Buy : %s | %s | %s' % (
                                    gamer_name, item_category, item_damage))

                                self.send_chat_msg('%s just bought a %s %s!' % (_user.nick, item_type, item_category))
                        
    """
    :::::::::::::::::::::::::::::::::::::::::::::::::::::BETTING:::::::::::::::::::::::::::::::::::::::::::::::::::::
    """    
    def do_bet(self, bet_sum, bet_clr):

        _user = self.users.search_by_nick(self.active_user.nick)
        gamer_name = _user.account
        coins = self.bc_check(_user.account)
        
        if self.is_client_mod:  
            bet_clr = bet_sum.split()
            length_b = len(bet_clr)
            
            if length_b < 1:
                self.send_chat_msg('You forgot to place bet!')
                bet_color = '0'
            elif length_b < 2:
                self.send_chat_msg('You forgot to pick a color!')
                bet_color = '0'
            else:
                bet_num = bet_clr[0]
                digitcheck = bet_num.isdigit()

                if digitcheck == False:
                    self.send_chat_msg('You can only bet numbers!')
                    bet_color = '0'
                else:
                    bet_color = bet_clr[1]
                if digitcheck == True and (bet_color == 'black' or bet_color == 'red'):

                    bet_amt = int(bet_num)
                    if coins == 0:
                        self.send_chat_msg('⛔ You\'re Broke!')
                    elif coins < bet_amt:
                        self.send_chat_msg('Insufficient Funds! \n %s\'s BRUHcoins: 💰%s' % (_user.nick, coins))
                    else:
                        db = pickledb.load(userdb, False)
                        time.sleep(1)
                        bet_type = ['black','red']
                        bet_choices = ['0','1','2','3','4','5','6','7','8','9','10']

                        b_type = random.choice(bet_type)
                        if str(b_type) == str(bet_color):

                            f_sum = bet_amt + coins
                            
                            user = {'bruhcoins': f_sum,
                                    'lastcoin': time.time()}
                            db.dadd('gamers', (gamer_name, user))
                            db.dump()
                            
                            if b_type == 'black':
                                c_emoji = ['♠️','♣️']
                                card_emoji = random.choice(c_emoji)
                            else:
                                c_emoji = ['♦','♥️']
                                card_emoji = random.choice(c_emoji)
                         

                            self.console_write(pinylib.COLOR['cyan'], '[User] New Bet Won : %s : %s' % (
                                gamer_name, f_sum))
                            self.send_chat_msg('%s It\'s %s! \n -- %s won 💰%s!' % (card_emoji, b_type, _user.nick, bet_amt))
                        else:
                            f_sum = coins - bet_amt 
                            
                            user = {'bruhcoins': f_sum,
                                    'lastcoin': time.time()}
                            db.dadd('gamers', (gamer_name, user))
                            db.dump()
                            
                            if b_type == 'red':
                                c_emoji = ['♦','♥️']
                                card_emoji = random.choice(c_emoji)
                            else:
                                c_emoji = ['♠️','♣️']
                                card_emoji = random.choice(c_emoji)
                         

                            self.console_write(pinylib.COLOR['cyan'], '[User] New Bet Lost : %s : %s' % (
                                gamer_name, f_sum))
                            self.send_chat_msg('%s It\'s %s! \n -- %s lost 💰%s!' % (card_emoji, b_type, _user.nick, bet_amt))

                
    def do_remove_gamer(self, gamer_name):

        if self.is_client_mod:
            if len(gamer_name) is 0:
                self.send_chat_msg('Missing account.')
            else:
                db = pickledb.load(userdb, False)
                if self.bc_check(gamer_name) > 0:
                    db.dpop('gamers', gamer_name)
                    db.dump()
        
                    self.send_chat_msg(
                        '%s gamer values cleared.' % gamer_name)
                else:
                    self.send_chat_msg(
                        '%s has no gamer profile!' % gamer_name)

    def do_remove_verified(self, verified_account):

        if self.is_client_mod:
            if len(verified_account) is 0:
                self.send_chat_msg('Missing account.')
            else:
                db = pickledb.load(userdb, False)
                if self.user_check(verified_account) == 5 or  self.user_check(verified_account) == 4:
                    db.dpop('users', verified_account)
                    db.dump()
        
                    self.send_chat_msg(
                        'Account %s lost all powers!' % verified_account)
                else:
                    self.send_chat_msg(
                        'Account %s has no power here!' % verified_account)

    def user_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('users', account):
            user = db.dget('users', account)
            return user['level']
        else:
            return 0
            
    def bc_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('gamers', account):
            user = db.dget('gamers', account)
            return user['bruhcoins']
        else:
            return 0
            
    def pole_type_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('fishing_poles', account):
            user = db.dget('fishing_poles', account)
            return user['pole_type']
        else:
            return 0
            
    def pole_level_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('fishing_poles', account):
            user = db.dget('fishing_poles', account)
            return user['pole_level']
        else:
            return 0
            
    def weapon_damage_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('weapons', account):
            user = db.dget('weapons', account)
            return user['weapon_damage']
        else:
            return 0
            
    def weapon_level_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('weapons', account):
            user = db.dget('weapons', account)
            return user['weapon_level']
        else:
            return 0
            
    def weapon_type_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('weapons', account):
            user = db.dget('weapons', account)
            return user['weapon_type']
        else:
            return 0
            
    def weapon_class_check(self, account):
        db = pickledb.load(userdb, False)
        if db.dexists('weapons', account):
            user = db.dget('weapons', account)
            return user['weapon_class']
        else:
            return 0

    def word_check(self, word):
        db = pickledb.load(userdb, False)
        if db.dexists('badwords', word):
            user = db.dget('badwords', word)
            return True
        else:
            return False

    def nick_check(self, nick):
        db = pickledb.load(userdb, False)
        if db.dexists('badnicks', nick):
            user = db.dget('badnicks', nick)
            return True
        else:
            return False

    def do_chatmod(self, verified_name):

        if self.is_client_mod:
            if len(verified_name) is 0:
                self.send_chat_msg('Account can\'t be blank.')
            elif len(verified_name) < 3:
                self.send_chat_msg('Account too short: ' +
                                   str(len(verified_name)))
            elif self.user_check(verified_name) == 4:
                self.send_chat_msg('%s is already in list.' % verified_name)
            else:

                db = pickledb.load(userdb, False)
                if self.user_check(verified_name) > 0:
                    db.dpop('users', verified_name)

                user = {'level': 4, 'by': self.active_user.account,
                        'created': time.time()}
                db.dadd('users', (verified_name, user))
                db.dump()
               

                self.send_chat_msg('%s is a chatmod now.' % verified_name)

    def do_remove_chatmod(self, verified_account):
        if self.is_client_mod:
            if len(verified_account) is 0:
                self.send_chat_msg('Missing account.')
            else:

                if self.user_check(verified_account) == 4:
                    db = pickledb.load(userdb, False)
                    db.dpop('users', verified_account)
                    db.dump()

                    self.send_chat_msg(
                        '%s is not a chatmod anymore.' % verified_account)
                else:
                    self.send_chat_msg(
                        'Account %s is not chatmod accounts.' % verified_account)

    def do_chatadmin(self, verified_name):

        if self.is_client_mod:
            if len(verified_name) is 0:
                self.send_chat_msg('Account can\'t be blank.')
            elif len(verified_name) < 3:
                self.send_chat_msg('Account too short: ' +
                                   str(len(verified_name)))

            elif self.user_check(verified_name) == 2:
                self.send_chat_msg('%s is already in list.' % verified_name)
            else:
                db = pickledb.load(userdb, False)
                if self.user_check(verified_name) == 4 or self.user_check(verified_name) == 9 or self.user_check(verified_name) == 5:
                    db.dpop('users', verified_name)

                user = {'level': 2, 'by': self.active_user.account,
                        'created': time.time()}
                db.dadd('users', (verified_name, user))
                db.dump()
                
                self.send_chat_msg('%s is an admin now.' % verified_name)

    def do_remove_chatadmin(self, verified_account):
        if self.is_client_mod:
            if len(verified_account) is 0:
                self.send_chat_msg('Missing account.')
            else:

                if self.user_check(verified_account) == 2:
                    db = pickledb.load(userdb, False)
                    db.dpop('users', verified_account)
                    db.dump()
                   
                    self.send_chat_msg(
                        '%s is not an admin anymore.' % verified_account)

    def do_cam_approve(self, user_name):
        """
        Allow a user to broadcast in a green room enabled room.

        :param user_name:  The name of the user allowed to broadcast.
        :type user_name: str
        """
        _user = self.users.search_by_nick(user_name)
        if len(user_name) > 0:
            if _user.is_waiting:
                self.send_cam_approve_msg(_user.id)
                _user.is_broadcasting = True
        else:
            self.send_chat_msg('No user named: %s' % user_name)

    def do_close_broadcast(self, user_name):
        """
        Close a users broadcast.

        :param user_name: The name of the user to close.
        :type user_name: str
        """
        if self.is_client_mod:
            if len(user_name) == 0:
                self.send_chat_msg('Mising user name.')
            else:
                _user = self.users.search_by_nick(user_name)
                if _user is not None and _user.is_broadcasting:
                    self.send_close_user_msg(_user.id)
                else:
                    self.send_chat_msg('No user named: %s' % user_name)

    def do_playlist_status(self):
        """ Shows the playlist queue. """
        if self.is_client_mod:
            if len(self.playlist.track_list) == 0:
                self.send_chat_msg('The playlist is empty.')
            else:
                queue = self.playlist.queue
                if queue is not None:
                    self.send_chat_msg('%s items in the playlist, %s still in queue.' %
                                       (queue[0], queue[1]))

    def do_next_tune_in_playlist(self):
        """ Shows the next track in the playlist. """
        if self.is_client_mod:
            if self.playlist.is_last_track is None:
                self.send_chat_msg('The playlist is empty.')
            elif self.playlist.is_last_track:
                self.send_chat_msg('This is the last track.')
            else:
                pos, next_track = self.playlist.next_track_info()
                if next_track is not None:
                    self.send_chat_msg('(%s) %s %s' %
                                       (pos, next_track.title, self.format_time(next_track.time)))

    def do_now_playing(self):
        """ Shows what track is currently playing. """
        if self.is_client_mod:
            if self.playlist.has_active_track:
                track = self.playlist.track
                if len(self.playlist.track_list) > 0:
                    self.send_private_msg(self.active_user.id,
                                          '(%s) %s %s' % (self.playlist.current_index, track.title,
                                                          self.format_time(track.time)))
                else:
                    self.send_private_msg(self.active_user.id, '%s %s' %
                                          (track.title, self.format_time(track.time)))
            else:
                self.send_private_msg(
                    self.active_user.nick, 'No track playing.')

    def do_who_plays(self):
        """ Show who requested the currently playing track. """
        if self.is_client_mod:
            if self.playlist.has_active_track:
                track = self.playlist.track
                ago = self.format_time(
                    int(pinylib.time.time() - track.rq_time))
                self.send_chat_msg(
                    '%s requested this track %s ago.' % (track.owner, ago))
            else:
                self.send_chat_msg('No track playing.')

    def do_help(self):
        """ Posts user level based command lists. """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)
        
        if self.active_user.user_level < 6:
            time.sleep(1)
            self.send_chat_msg(
                                     '▂▅▇ Public Cmds  ▇▅▂ \n \n !urb <word> \n !wea <zipcode>\n !chuck, !8ball <question>, !roll, !flip')
            time.sleep(2)
            self.send_chat_msg(
                                     '▂▅▇ Toke Cmds  ▇▅▂ \n \n !tokes, !cheers, !join')
        if self.active_user.user_level < 5 or _level == 5 or _level == 4:
            time.sleep(3)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Youtube Cmds  ▇▅▂ \n \n !yt, !close, !seek, !reset, !spl, !del, !skip, !yts, !rpl, !pause, !play, !pyst, !whatsong, !status, !now, !whoplayed')
            time.sleep(4)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Game Cmds  ▇▅▂ \n \n !fish, !bet <#> <black/red>, !advtime')
        if self.active_user.user_level < 5 or _level == 4:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Mod Cmds  ▇▅▂ \n \n !mod <account> : can add other bruh\'s \n !bruh <account> : youtube powers \n !rmv, !clr, !kick, !ban \n !cam <SCREENname> \n !close \n !bada  <account> \n !banw <badword> \n !rmw <badword> \n !rmbad <account> \n !badn <nick>')
        if self.active_user.user_level < 4:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Admin Cmds  ▇▅▂ \n \n !lockdown (noguests) \n !lockup(password enabled) \n !chatmod \n !dechatmode \n !noguest')
    def do_help_pm(self):
        """ Posts user level based command lists. """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)
        
        if self.active_user.user_level < 6:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Public Cmds  ▇▅▂ \n \n !urb <word> \n !wea <zipcode>\n !chuck, !8ball <question>, !roll, !flip')
            time.sleep(2)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Toke Cmds  ▇▅▂ \n \n !tokes, !cheers, !join')
        if self.active_user.user_level < 5 or _level == 5 or _level == 4:
            time.sleep(3)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Youtube Cmds  ▇▅▂ \n \n !yt, !close, !seek, !reset, !spl, !del, !skip, !yts, !rpl, !pause, !play, !pyst, !whatsong, !status, !now, !whoplayed')
            time.sleep(4)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Game Cmds  ▇▅▂ \n \n !fish, !bet <#> <black/red>, !advtime')
        if self.active_user.user_level < 5 or _level == 4:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Mod Cmds  ▇▅▂ \n \n !mod <account> : can add other bruh\'s \n !bruh <account> : youtube powers \n !rmv, !clr, !kick, !ban, !cam <SCREENname> \n !close \n !bada  <account> \n !banw <badword> \n !rmw <badword> \n !rmbad <account> \n !badn <nick>')
        if self.active_user.user_level < 4:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '▂▅▇ Admin Cmds  ▇▅▂ \n \n !lockdown (noguests) \n !lockup(password enabled) \n !chatmod \n !dechatmode \n !noguest')
                
 
                
    def do_script_level(self):
        """
        Posts user level based command lists.
        """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)  
        
        if self.active_user.user_level < 8:
            time.sleep(1)
            self.send_chat_msg('TC Level : %s | BRUH Level : %s' % (_user.user_level, _level))
            
    def do_level(self):
        """
        Posts user level based command lists.
        """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)
        coins = self.bc_check(_user.account) 
        pole_type = self.pole_type_check(_user.account)
        pole_level = self.pole_level_check(_user.account)
        
        weapon_class = self.weapon_class_check(_user.account)
        weapon_level = self.weapon_level_check(_user.account)
        weapon_type = self.weapon_type_check(_user.account)
        weapon_damage = self.weapon_damage_check(_user.account)
        
        
        if self.active_user.user_level < 5 or _level == 5 or _level == 4:
            time.sleep(1)
            if weapon_level == 0:
                weapon_lvl = 'No Weapon Equipped!'
            else:
                weapon_lvl = ('%s %s : %s Dmg' % (weapon_type, weapon_class, weapon_damage))
            if pole_level == 0:
                pole_lvl = 'No Pole Equipped!'
            else:
                pole_lvl = ('%s Pole' % (pole_type))

            self.send_chat_msg('▂▅▇ 🏦 %s\'s Inventory \n \n 💰 %s BRUHcoins \n 🎣 %s \n ⚔️ %s' % (_user.nick, coins, pole_lvl, weapon_lvl))
            
    def do_pole_type(self):
        """
        Posts user level based command lists.
        """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)
        pole_type = self.pole_check(_user.account)
        
        if self.active_user.user_level < 5 or _level == 5 or _level == 4:
            time.sleep(1)
            if pole_type == 1:
                self.send_chat_msg('%s uses pole type %s : a wooden pole.' % (_user.nick, pole_type))
            elif pole_type == 2:
                self.send_chat_msg('%s uses pole type %s : a steel pole.' % (_user.nick, pole_type))
            elif pole_type == 3:
                self.send_chat_msg('%s uses pole type %s : a bamboo pole.' % (_user.nick, pole_type))
            else:
                self.send_chat_msg('%s uses a twig and string as thier pole. \n !store to purchase a better one!' % (_user.nick))
            
    def do_advtime(self): 
        """
        Posts user level based command lists.
        """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)  
        
        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'Intro 1: After a drunken night out with friends, you awaken the next morning in a thick, dank forest. Head spinning and fighting the urge to vomit, you stand and marvel at your new, unfamiliar setting. The peace quickly fades when you hear a grotesque sound emitting behind you. A slobbering orc is running towards you. You will:')
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '!rock \n ◾ Throw a nearby rock \n \n !lay \n ◾ Lie down and cry \n \n !run \n ◾ Start Running')
                
    def answer_rock(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'The orc is stunned, but regains control. He begins running towards you again. Will you:')
            self.send_private_msg(
                self.active_user.id, '!run \n ◾ Run \n \n !anotherrock \n ◾ Throw another rock \n \n !cave \n ◾ Run towards a nearby cave')
                
    def answer_lay(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'Welp, that was quick. \n \n You died!')
            self.send_chat_msg('%s was killed by an orc, because they just laid down n\' cried. !' % (self.active_user.nick)) 
                
    def answer_another_rock(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You decided to throw another rock, as if the first rock thrown did much damage. The rock flew well over the orcs head. You missed. \n \n You died!')
            self.send_chat_msg('%s died trying to stone an orc!' % (self.active_user.nick))
                
    def answer_cave(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You were hesitant, since the cave was dark and ominous. Before you fully enter, you notice a shiny sword on the ground.')

            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'Do you pick up the sword? \n \n !sword \n \n !nosword')

    def answer_sword(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '🗡️ Sword Aquired.')
            self.send_private_msg(
                self.active_user.id, 'What do you do next?')
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '!hide \n !swordfight \n !flee ')

    def answer_nosword(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'What do you do next?')
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '!hide \n !fight \n !flee ')
                
    def answer_sword_fight(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, '⚔️ You laid in wait. The shimmering sword attracts the orc. As he walked closer and closer, your heart beat rapidly. The orc reaches out to grab the sword, you thrust forward, and pierce the blade into its chest. \n \n You survived!')
            self.send_chat_msg('%s killed an orc with a sword!' % (self.active_user.nick)) 
                
    def answer_fight(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You should have picked up that sword or maybe the flower. You\'re defenseless. \n \n You died!')
            self.send_chat_msg('%s was killed by an orc!' % (self.active_user.nick)) 
                
    def answer_run(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You run as quickly as possible, but the orc\'s speed is too great. You then:')
            self.send_private_msg(
                self.active_user.id, '!boulder \n ◾ Hide behind boulder \n \n !brawl \n ◾ Raise your fist \n \n !town \n ◾ Run into an abandoned town')
                
    def answer_duck(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You duck as quickly as possible, but the orc still sees you . You then:')
            self.send_private_msg(
                self.active_user.id, '!boulder \n ◾ Hide behind a boulder \n \n !brawl \n ◾ Raise your fist \n \n !cave \n ◾ Run towards a nearby cave')
                
    def answer_town(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'While frantically running, you notice a rusted sword lying in the mud. You quickly reach down and grab it, but miss. You try to calm your heavy breathing as you hide behind a delapitated building, waiting for the orc to come charging around the corner. You notice a purple flower near your foot.')
            self.send_private_msg(
                self.active_user.id, 'Do you pick it up? 🌺 \n \n !flower \n \n !noflower')
                
    def answer_flower(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You quickly hold out the 🌺, somehow hoping it will stop the orc. It does! The orc was looking for love. \n \n This got weird, but you survived!')
            self.send_chat_msg('%s survived an orc attack, by becoming the orcs friend!' % (self.active_user.nick))

    def answer_no_flower(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You hear its heavy footsteps and ready yourself for the impending orc.') 
            self.send_private_msg(
                self.active_user.id, 'The town is empty, the buildings are barely standing. You hear the orc grow closer. \n You decide to:') 
            self.send_private_msg(
                self.active_user.id, '!brawl \n ◾ Raise your fist \n \n !hide ◾ Hide in a dark corner \n \n !duck \n ◾ Duck for cover') 

    def answer_flee(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'As the orc enters the dark cave, you sliently sneak out. You\'re several feet away, but the orc turns around and sees you running.')
            self.answer_run()
                
    def answer_hide(self):
        
        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'Really? You\'re going to hide in the dark? I think orcs can see very well in the dark, right? Not sure, but I\'m going with YES, so... \n \n You died!')
            self.send_chat_msg('%s died while hiding from an orc in the dark!' % (self.active_user.nick))
                
    def answer_boulder(self):

        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You\'re easily spotted. \n \n You died!')
            self.send_chat_msg('%s died while hiding from an orc behind a boulder!' % (self.active_user.nick))
                
    def answer_brawl(self):
        """
        fist fight an orc.
        """
        
        if self.active_user.user_level < 5:
            self.send_chat_msg('%s died trying to fist fight an orc!' % (self.active_user.nick))
            time.sleep(1)
            self.send_private_msg(
                self.active_user.id, 'You\'re no match for an orc. \n \n You died!')

                
    def do_stan(self):
        """
        Stann command.
        """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)  
        
        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_chat_msg('%s is requesting STAN to toke!' % (_user.nick))
                
    def do_stan_pm(self):
        """
        Stann command.
        """
        _user = self.users.search_by_nick(self.active_user.nick)
        _level = self.user_check(_user.account)  
        
        if self.active_user.user_level < 5:
            time.sleep(1)
            self.send_private_msg(
                'smokeyllama', '%s is requesting you to toke!' % (_user.nick))
  
    def do_play_youtube(self, search_str):
        """ 
        Plays a youtube video matching the search term.

        :param search_str: The search term.
        :type search_str: str
        """
        log.info('user: %s:%s is searching youtube: %s' %
                 (self.active_user.nick, self.active_user.id, search_str))
        if self.is_client_mod:
            if len(search_str) is 0:
                self.send_chat_msg('Please specify youtube title, id or link.')
            else:
                _youtube = youtube.search(search_str)
                if _youtube is None:
                    log.warning('youtube request returned: %s' % _youtube)
                    self.send_chat_msg('Could not find video: ' + search_str)
                else:
                    log.info('youtube found: %s' % _youtube)
                    if self.playlist.has_active_track:
                        track = self.playlist.add(
                            self.active_user.nick, _youtube)
                        self.send_chat_msg('(%s) %s %s' %
                                           (self.playlist.last_index, track.title, self.format_time(track.time)))
                    else:
                        track = self.playlist.start(
                            self.active_user.nick, _youtube)
                        self.send_yut_play(track.id, track.time, track.title)
                        self.timer(track.time)

    def do_search_urban_dictionary(self, search_str):
        """ 
        Shows urbandictionary definition of search string.

        :param search_str: The search string to look up a definition for.
        :type search_str: str
        """
        if self.is_client_mod:
            if len(search_str) is 0:
                self.send_chat_msg('Please specify something to look up.')
            else:
                urban = other.urbandictionary_search(search_str)
                if urban is None:
                    self.send_chat_msg(
                        'Could not find a definition for: %s' % search_str)
                else:
                    if len(urban) > 70:
                        chunks = pinylib.string_util.chunk_string(urban, 70)
                        for i in range(0, 2):
                            self.send_chat_msg(chunks[i])
                    else:
                        self.send_chat_msg(urban)
    def do_porn_search(self, searchterm_str):
        """ 
        Shows urbandictionary definition of search string.

        :param search_str: The search string to look up a definition for.
        :type search_str: str
        """
        if len(searchterm_str) is 0:
            self.send_chat_msg('Please specify a p to search for.')
        else:
            porn = other.porn_search(searchterm_str)
            if porn is None:
                self.send_chat_msg(
                    'Could not find p data for: %s' % searchterm_str)
            else:
                self.send_chat_msg(porn)

    def do_weather_search(self, search_str):
        """ 
        Shows weather info for a given search string.

        :param search_str: The search string to find weather data for.
        :type search_str: str
        """
        if len(search_str) is 0:
            self.send_chat_msg('Please specify a city to search for.')
        else:
            weather = other.weather_search(search_str)
            if weather is None:
                self.send_chat_msg(
                    'Could not find weather data for: %s' % search_str)
            else:
                self.send_chat_msg(weather)

    # == Just For Fun Command Methods. ==
    def do_chuck_noris(self):
        """ Shows a chuck norris joke/quote. """
        chuck = other.chuck_norris()
        if chuck is not None:
            self.send_chat_msg(chuck)

    def do_8ball(self, question):
        """ 
        Shows magic eight ball answer to a yes/no question.

        :param question: The yes/no question.
        :type question: str
        """
        if len(question) is 0:
            self.send_chat_msg('Question.')
        else:
            self.send_chat_msg('8Ball %s' % locals_.eight_ball())

    def do_dice(self):
        """ roll the dice. """
        self.send_chat_msg('The dice rolled: %s' % locals_.roll_dice())

    def do_flip_coin(self):
        """ Flip a coin. """
        self.send_chat_msg('The coin was: %s' % locals_.flip_coin())

    def tokesession(self, cmd_args):

        prefix = pinylib.CONFIG.B_PREFIX

        if cmd_args == "!!":
            if self.active_user.user_level < 5:
                self.resettokes()
                self.send_chat_msg('cнeerѕ нαѕ вeeɴ reѕeт!')
            return

        if self.toke_mode:
            mins = self.until(self.toke_start, self.toke_end)

            if self.active_user.nick in self.tokers:
                self.send_chat_msg(
                    '✋ You have already joined! \n %s %s to cheers...' % (str(mins), self.pluralize('min', mins)))
            else:
                self.newtoker()
            return
        else:
            if self.active_user.user_level < 6:
                try:
                    end = int(cmd_args)
                    if not 1 <= end <= 10:
                        raise Exception()
                except:
                    self.send_chat_msg('▂▅▇ 🔥 CHEERS BITCHES 🔥 ▇▅▂')
                    return

                announce = 1
                self.tokers.append(self.active_user.nick)
                self.startTokes(end, announce)
                mins = self.until(self.toke_start, self.toke_end)
                self.send_chat_msg(
                    '⌛ %s %s until the cheers! \n Type %sjoin to join the session!' % (
                        str(mins), self.pluralize('min', mins), prefix))

    def newtoker(self):
        joinicon = ['💨', '☁', '🍄', '🔥']
        self.tokers.append(self.active_user.nick)
        mins = self.until(self.toke_start, self.toke_end)
        time.sleep(0.9)
        self.send_chat_msg('%s %s is ready to toke down! \n ⌛ %s %s left for cheers' % (
            random.choice(joinicon), self.active_user.nick, str(mins), self.pluralize('min', mins)))
        return
        
    def startTokes(self, end, announce=0):
        self.toke_mode = True
        t = int(time.time())
        self.announce = int(announce) * 60
        self.announceCheck = t + self.announce
        self.toke_start = t
        self.toke_end = int(end) * 60
        thread = threading.Thread(target=self.toke_count, args=())
        thread.daemon = True
        thread.start()

    def resettokes(self):
        self.toke_mode = False
        self.announce = 0
        self.announceCheck = 0
        self.tokers[:] = []
        self.toke_start = 0
        self.toker = None
        return

    def toke_count(self):
        prefix = pinylib.CONFIG.B_PREFIX
        while True:
            time.sleep(0.3)
            t = time.time()

            if not self.toke_mode:
                time.sleep(5)
                break

            if self.toker is None:
                self.toker = str(self.tokers[0])

            if t > self.toke_start + self.toke_end:
                start = int((t - self.toke_start) / 60)

                if len(self.tokers) > 1:
                    if len(self.tokers) == 2:
                        joined = self.tokers[1]
                    else:
                        joined = ''
                        j = 0
                        for name in self.tokers[1:]:
                            if j == len(self.tokers) - 2:
                                joined += 'and ' + name
                            else:
                                joined += name + ', '
                            j += 1

                    fuckinggrammar = 'is'
                    if len(self.tokers) > 2:
                        fuckinggrammar = 'are'

                    self.send_chat_msg(
                        '%s called cheers %s %s ago! \n %s %s taking part... \n \n ▂▅▇ 🔥 CHEERS BITCHES 🔥 ▇▅▂'
                        % (self.toker, start, self.pluralize('min', start), joined,
                           fuckinggrammar))
                else:
                    self.send_chat_msg(
                        '%s, called cheers %s %s ago! \n Nobody joined in... fuck it! \n \n ▂▅▇ 🔥 CHEERS BITCHES 🔥 ▇▅▂'
                        % (self.toker, start, self.pluralize('min', start)))
                self.resettokes()
                break

            if t > self.announceCheck:
                self.announceCheck = t + self.announce

                start = int((t - self.toke_start) / 60)
                self.send_chat_msg('⌛ %s called a cheers %s %s ago! \n %scheers to join now!' % (
                     self.toker, str(start), self.pluralize("min", start), prefix))

    @staticmethod
    def pluralize(text, n, pluralForm=None):
        if n != 1:
            if pluralForm is None:
                text += 's'
        return text

    @staticmethod
    def until(start, end):
        t = int(time.time())
        d = int(round(float(start + end - t) / 60))
        if d == 0:
            d = 1
        return d
        
    def private_message_handler(self, private_msg):
        """
        Private message handler.

        Overrides private_message_handler in pinylib
        Overrides private_message_handler in pinylib
        to enable private commands.

        :param private_msg: The private message.
        :type private_msg: str
        """
        # Split the message in to parts.
        # parts[0] is the command..
        # The rest is a command argument.
        
        prefix = pinylib.CONFIG.B_PREFIX
        
        pm_parts = private_msg.split(' ')
        pm_cmd = pm_parts[0].lower().strip()
        pm_arg = ' '.join(pm_parts[1:]).strip()
            
        if self.is_client_owner:

            if pm_cmd == prefix + 'help':
                self.do_help_pm()
                
            elif pm_cmd == prefix + 'rock':
                self.answer_rock()
            elif pm_cmd == prefix + 'lay':
                self.answer_lay()
            elif pm_cmd == prefix + 'anotherrock':
                self.answer_another_rock()
            elif pm_cmd == prefix + 'cave':
                self.answer_cave()
            elif pm_cmd == prefix + 'sword':
                self.answer_sword()
            elif pm_cmd == prefix + 'nosword':
                self.answer_nosword()
            elif pm_cmd == prefix + 'swordfight':
                self.answer_sword_fight()
            elif pm_cmd == prefix + 'fight':
                self.answer_fight()
            elif pm_cmd == prefix + 'run':
                self.answer_run()
            elif pm_cmd == prefix + 'town':
                self.answer_town()
            elif pm_cmd == prefix + 'flower':
                self.answer_flower()
            elif pm_cmd == prefix + 'noflower':
                self.answer_no_flower()
            elif pm_cmd == prefix + 'flee':
                self.answer_flee()
            elif pm_cmd == prefix + 'hide':
                self.answer_hide()
            elif pm_cmd == prefix + 'boulder':
                self.answer_boulder()
            elif pm_cmd == prefix + 'brawl':
                self.answer_brawl()
            elif pm_cmd == prefix + 'duck':
                self.answer_duck()

            elif pm_cmd == prefix + 'stan':
                    self.do_stan_pm()

        self.console_write(pinylib.COLOR['white'], '[PRIMSG] %s: %s' % (
            self.active_user.nick, private_msg))



    def timer_event(self):
        """ This gets called when the timer has reached the time. """
        if len(self.playlist.track_list) > 0:
            if self.playlist.is_last_track:
                if self.is_connected:
                    self.send_chat_msg('Resetting playlist.')
                self.playlist.clear()
            else:
                track = self.playlist.next_track
                if track is not None and self.is_connected:
                    self.send_yut_play(track.id, track.time, track.title)
                self.timer(track.time)

    def timer(self, event_time):
        """
        Track event timer.

        This will cause an event to occur once the time is done.

        :param event_time: The time in seconds for when an event should occur.
        :type event_time: int | float
        """
        self.timer_thread = threading.Timer(event_time, self.timer_event)
        self.timer_thread.start()

    def cancel_timer(self):
        """ Cancel the track timer. """
        if self.timer_thread is not None:
            if self.timer_thread.is_alive():
                self.timer_thread.cancel()
                self.timer_thread = None
                return True
            return False
        return False

    def options(self):
        """ Load/set special options. """

        log.info('options: is_client_owner: %s, is_client_mod: %s' %
                 (self.is_client_owner, self.is_client_mod))

        if self.is_client_owner:
            self.get_privacy_settings()

        if self.is_client_mod:
            self.send_banlist_msg()

    def get_privacy_settings(self):
        """ Parse the privacy settings page. """
        log.info('Parsing %s\'s privacy page.' % self.account)
        self.privacy_ = privacy.Privacy(proxy=None)
        self.privacy_.parse_privacy_settings()

    @staticmethod
    def format_time(time_stamp, is_milli=False):
        """ 
        Converts a time stamp as seconds or milliseconds to (day(s)) hours minutes seconds.

        :param time_stamp: Seconds or milliseconds to convert.
        :param is_milli: The time stamp to format is in milliseconds.
        :return: A string in the format (days) hh:mm:ss
        :rtype: str
        """
        if is_milli:
            m, s = divmod(time_stamp / 1000, 60)
        else:
            m, s = divmod(time_stamp, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        if d == 0 and h == 0:
            human_time = '%02d:%02d' % (m, s)
        elif d == 0:
            human_time = '%d:%02d:%02d' % (h, m, s)
        else:
            human_time = '%d Day(s) %d:%02d:%02d' % (d, h, m, s)
        return human_time

    def check_msg(self, msg):
        """ 
        Checks the chat message for ban string.

        :param msg: The chat message.
        :type msg: str
        """

        global lastmsgs
        global spam
        global spammer

        should_be_banned = False
        is_a_spammer = False

        chat_words = msg.split(' ')

        # if flooded or a long text

        total = sum(char.isspace() or char == "0" for char in msg)

        if total > 140 and self.active_user.nick == spammer:
            spammer = 0
            self.console_write(pinylib.COLOR[
                               'bright_yellow'], '[Security] Spam - banned %s.' % (self.active_user.nick))
            if self.active_user.user_level > 4:
                self.send_ban_msg(self.active_user.id)
        elif total > 140:
            spammer = self.active_user.nick
            self.console_write(pinylib.COLOR[
                               'bright_yellow'], '[Security] Spam: Long message - %s by %s' % (total, self.active_user.nick))
            if self.active_user.user_level > 4:
                self.send_kick_msg(self.active_user.id)

        for word in chat_words:
            if self.word_check(word):
                should_be_banned = True

        if self.active_user.user_level > 5:

            if len(lastmsgs) is 0:
                lastmsgs.append(msg)
                self.console_write(
                    pinylib.COLOR['bright_yellow'], '[Security] Spam: Protection on.')

            else:
                msg_count = str(len(lastmsgs))
                self.console_write(pinylib.COLOR[
                                   'bright_yellow'], '[Security] Spam: Processing - %s' % (msg_count))

                if msg in lastmsgs:
                    spam += 1
                    lastmsgs.append(msg)
                    spammer = self.active_user.nick
                    self.console_write(pinylib.COLOR[
                                       'bright_yellow'], '[Security] Spam: Found Spammer %s' % (self.active_user.nick))
                else:
                    lastmsgs.append(msg)

            if spam > 1:
                should_be_banned = True
                is_a_spammer = True
                spammer = 0
                spam = 0
                del lastmsgs[:]
                lastmsgs = []

            if len(lastmsgs) > 8:
                del lastmsgs[:]
                lastmsgs = []
                spam = 0
                spammer = 0
                self.console_write(
                    pinylib.COLOR['bright_yellow'], '[Security] Spam: Resetting last message db.')

        if should_be_banned:
            if self.active_user.user_level == 6:
                if is_a_spammer:
                    self.do_bad_account(self.active_user.account)
                    is_a_spammer = False
                self.send_ban_msg(self.active_user.id)
            elif len(self.active_user.account) is 0:
                if is_a_spammer:
                    is_a_spammer = False
                self.send_ban_msg(self.active_user.id)

            self.console_write(pinylib.COLOR['cyan'], '[Security] Spam: Flood, Repeat or Badword by %s' % (self.active_user.nick))