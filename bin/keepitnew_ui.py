"""KeepItNew appearance, settings and widget helpers. No external dependencies."""
import json,os,tempfile
from pathlib import Path
from functools import lru_cache
APP='updates'
VERSION = '0.1.2'
APP_NAME='KeepItNew'
THEMES={
 'Nord':('2e3440','eceff4','88c0d0','b48ead','a3b1c6','434c5e','a3be8c','bf616a'),
 'Catppuccin Mocha':('1e1e2e','cdd6f4','89b4fa','cba6f7','a6adc8','45475a','a6e3a1','f38ba8'),
 'Tokyo Night':('1a1b26','c0caf5','7aa2f7','bb9af7','9aa5ce','292e42','9ece6a','f7768e'),
 'Gruvbox Dark':('282828','ebdbb2','83a598','d3869b','a89984','504945','b8bb26','fb4934'),
 'Dracula':('282a36','f8f8f2','8be9fd','bd93f9','a4a5b8','44475a','50fa7b','ff5555'),
 'Rose Pine':('191724','e0def4','9ccfd8','c4a7e7','908caa','403d52','31748f','eb6f92'),
 'Solarized Dark':('002b36','93a1a1','2aa198','6c71c4','839496','073642','859900','dc322f'),
 'Solarized Light':('fdf6e3','586e75','268bd2','6c71c4','657b83','eee8d5','859900','dc322f'),
 'High Contrast':('000000','ffffff','00ffff','ff88ff','dddddd','333333','00ff00','ff7777'),
}
SETTINGS=Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))/'keepitnew/appearance.json'

_THEME_CACHE={}
def current():
 try:
  stamp=(str(SETTINGS),SETTINGS.stat().st_mtime_ns)
  if _THEME_CACHE.get('stamp')!=stamp:_THEME_CACHE.update(stamp=stamp,name=json.loads(SETTINGS.read_text()).get('theme','Nord'))
  name=_THEME_CACHE['name']
 except (OSError,ValueError,AttributeError):name='Nord'
 return name if isinstance(name,str) and name in THEMES else 'Nord'

def palette(name=None):return dict(zip(('background','text','accent','purple','dim','surface','green','red'),THEMES[name or current()]))

def save(name):
 if name not in THEMES:raise ValueError('Unknown theme')
 _write_json(SETTINGS,{'theme':name})



_COLOR_SESSION=0
_TERMINAL_PALETTE=None

from contextlib import contextmanager

@contextmanager
def terminal_session():
 """Keep app colors local to this terminal session and restore them on exit."""
 import sys
 global _COLOR_SESSION,_TERMINAL_PALETTE
 supported=sys.stdout.isatty() and bool(os.environ.get('KITTY_WINDOW_ID')) and not os.environ.get('TMUX')
 if supported:
  sys.stdout.write('\033]30001\033\\');sys.stdout.flush();_COLOR_SESSION+=1
 try:yield
 finally:
  if supported:
   sys.stdout.write('\033]30101\033\\');sys.stdout.flush();_COLOR_SESSION-=1;_TERMINAL_PALETTE=None

def run_screen(screen):
 import curses
 with terminal_session():return curses.wrapper(screen)

def kitty_launch_options():
 """Use an isolated app window; no global Kitty configuration is changed."""
 import uuid
 name=APP_NAME.lower()
 return ['-o','dynamic_background_opacity=yes','-o','allow_remote_control=socket-only',
         '--listen-on','unix:@'+name+'-'+uuid.uuid4().hex,
         '-o','env='+name.upper()+'_WINDOW=1']

def apply_opacity(value):
 import subprocess
 name=APP_NAME.lower();socket=os.environ.get('KITTY_LISTEN_ON','');window=os.environ.get('KITTY_WINDOW_ID','')
 if (os.environ.get(name.upper()+'_WINDOW')!='1' or not socket.startswith('unix:@'+name+'-') or not window.isdigit()):
  return 'Reopen from the widget or app launcher to apply opacity.'
 try:
  result=subprocess.run(['kitty','@','--to',socket,'set-background-opacity','--match','id:'+window,str(value)],
                        stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=3)
  if result.returncode==0:return 'Opacity applied to this window.'
 except (OSError,subprocess.TimeoutExpired):pass
 return 'Opacity saved; reopen the app window to apply it.'

def terminal_palette(p):
 import sys
 global _TERMINAL_PALETTE
 stamp=(p['text'],p['background'])
 if _COLOR_SESSION and stamp!=_TERMINAL_PALETTE:
  sys.stdout.write('\033]21;foreground=#'+p['text']+';background=#'+p['background']+'\033\\');sys.stdout.flush()
  _TERMINAL_PALETTE=stamp

def curses_colors(curses,win,name=None,personal_role=None):
 p=palette(name);terminal_palette(p)
 if personal_role in p:p['purple']=p[personal_role]
 try:
  # Define useful pairs even on terminals without mutable RGB colors.
  for pair,fg,bg in ((1,curses.COLOR_CYAN,-1),(2,curses.COLOR_WHITE,curses.COLOR_BLUE),
                     (3,curses.COLOR_WHITE,-1),(4,curses.COLOR_MAGENTA,-1),(5,curses.COLOR_WHITE,-1)):
   curses.init_pair(pair,fg,bg)
  if curses.can_change_color() and curses.COLORS>21:
   for i,key in enumerate(('accent','text','surface','background','purple','dim'),16):
    color=p[key];curses.init_color(i,*(round(int(color[n:n+2],16)*1000/255) for n in (0,2,4)))
   curses.init_pair(1,16,-1);curses.init_pair(2,17,18);curses.init_pair(3,17,-1);curses.init_pair(4,20,-1);curses.init_pair(5,21,-1)
  elif curses.COLORS>=256:
   def nearest(value):
    rgb=[int(value[i:i+2],16) for i in (0,2,4)]
    levels=(0,95,135,175,215,255)
    candidates=[(16+36*r+6*g+b,(levels[r],levels[g],levels[b])) for r in range(6) for g in range(6) for b in range(6)]
    candidates += [(232+i,(8+i*10,)*3) for i in range(24)]
    return min(candidates,key=lambda c:sum((a-b)**2 for a,b in zip(rgb,c[1])))[0]
   colors={key:nearest(value) for key,value in p.items()}
   for pair,fg,bg in ((1,'accent','background'),(2,'text','surface'),(3,'text','background'),(4,'purple','background'),(5,'dim','background')):
    curses.init_pair(pair,colors[fg],colors[bg] if pair==2 else -1)
  win.bkgd(' ',curses.color_pair(3))
 except curses.error:pass


def menu_frame(curses,win,app=None,values=None):
 """Square, theme-aware frame using the terminal's transparent background."""
 app=app or APP;values=values or options(app)
 h,w=win.getmaxyx()
 if h<5 or w<12:return
 style=values.get(app+'_border','single')
 edges={'single':('┌','┐','└','┘','─','│'),'double':('╔','╗','╚','╝','═','║'),'heavy':('┏','┓','┗','┛','━','┃'),'none':(' ',' ',' ',' ',' ',' ')}
 tl,tr,bl,br,line,side=frame(app,values)
 color=curses.color_pair({'accent':1,'purple':4,'dim':5}.get(values.get(app+'_border_color'),1))
 def write(y,x,text):
  try:win.addnstr(y,x,text,max(0,w-x),color)
  except curses.error:pass
 write(0,0,tl+line*(w-2)+tr);write(h-1,0,bl+line*(w-2)+br)
 for y in range(1,h-1):
  write(y,0,side)
  try:win.addch(y,w-1,side,color)
  except curses.error:pass

def select_option(curses,win,title,choices,current):
 selected=next((i for i,(value,_) in enumerate(choices) if value==current),0);offset=0
 while True:
  curses_colors(curses,win,choices[selected][0] if title.lower()=='theme' else None);win.erase();h,w=win.getmaxyx();menu_frame(curses,win)
  def put(y,text,style=0):
   if 0<y<h-1:
    try:win.addnstr(y,2,text,max(0,w-4),style)
    except curses.error:pass
  put(1,title.upper(),curses.color_pair(1)|curses.A_BOLD)
  count=max(1,h-7);offset=min(offset,selected)
  if selected>=offset+count:offset=selected-count+1
  for i,(value,label) in enumerate(choices[offset:offset+count],offset):
   text=('› ' if i==selected else '  ')+label+('  ✓' if value==current else '')
   put(3+i-offset,text.ljust(max(0,w-4)),curses.color_pair(2) if i==selected else 0)
  put(h-3,'↑↓ Choose · Enter Apply to draft · Esc Cancel',curses.color_pair(1))
  win.refresh();key=win.getch()
  if key in (27,3):return current
  if key==curses.KEY_MOUSE:
   try:_,x,y,_,state=curses.getmouse()
   except curses.error:continue
   if state & curses.BUTTON4_PRESSED:key=curses.KEY_UP
   elif state & getattr(curses,'BUTTON5_PRESSED',0):key=curses.KEY_DOWN
   elif state & (curses.BUTTON1_CLICKED|curses.BUTTON1_PRESSED) and 3<=y<3+min(count,len(choices)-offset):return choices[offset+y-3][0]
   else:continue
  if key in (10,13,32):return choices[selected][0]
  if key in (curses.KEY_DOWN,9):selected=(selected+1)%len(choices)
  elif key in (curses.KEY_UP,curses.KEY_BTAB):selected=(selected-1)%len(choices)
  elif key in (curses.KEY_NPAGE,curses.KEY_PPAGE):selected=max(0,min(len(choices)-1,selected+(count if key==curses.KEY_NPAGE else -count)))

def picker():
 import curses
 names=list(THEMES)
 def screen(win):
  selected=names.index(current());offset=0
  curses.curs_set(0);win.keypad(True);curses.start_color();curses.use_default_colors()
  curses.init_pair(1,curses.COLOR_CYAN,-1);curses.init_pair(2,curses.COLOR_WHITE,curses.COLOR_BLUE)
  curses.mousemask(curses.ALL_MOUSE_EVENTS);curses.mouseinterval(0)
  while True:
   curses_colors(curses,win,names[selected]);win.erase();h,w=win.getmaxyx();menu_frame(curses,win)
   def put(y,text,style=0):
    if 0<=y<h-1:
     try:win.addnstr(y,2,text,max(0,w-4),style)
     except curses.error:pass
   put(1,'KEEPITNEW / APPEARANCE',curses.color_pair(1))
   visible=max(1,h-7);offset=max(0,min(offset,selected))
   if selected>=offset+visible:offset=selected-visible+1
   for i,name in enumerate(names[offset:offset+visible]):put(3+i,('› ' if i+offset==selected else '  ')+name,curses.color_pair(2) if i+offset==selected else 0)
   hint='Enter Apply · N Nord · Esc Back' if w<70 else '↑↓ Preview · Enter/click Apply · N Nord · Esc Back'
   put(h-3,' '*max(0,(w-4-len(hint))//2)+hint,curses.color_pair(1))
   win.refresh();key=win.getch()
   if key in (27,ord('q')):return
   if key in (10,13):save(names[selected]);return
   if key==ord('n'):save('Nord');return
   if key in (curses.KEY_DOWN,ord('j')):selected=min(len(names)-1,selected+1)
   elif key in (curses.KEY_UP,ord('k')):selected=max(0,selected-1)
   elif key==curses.KEY_MOUSE:
    try:_,x,y,_,state=curses.getmouse()
    except curses.error:continue
    if state & curses.BUTTON4_PRESSED:selected=max(0,selected-1)
    elif state & getattr(curses,'BUTTON5_PRESSED',0):selected=min(len(names)-1,selected+1)
    elif state & (curses.BUTTON1_CLICKED|curses.BUTTON1_PRESSED) and 3<=y<3+min(visible,len(names)-offset):
     save(names[offset+y-3]);return
 run_screen(screen)

_PREF_CACHE={}
def preferences():
 path=SETTINGS.parent/'preferences.json'
 try:
  stamp=(str(path),path.stat().st_mtime_ns)
  if _PREF_CACHE.get('stamp')!=stamp:_PREF_CACHE.update(stamp=stamp,data=json.loads(path.read_text()))
  return _PREF_CACHE['data'] if isinstance(_PREF_CACHE['data'],dict) else {}
 except (OSError,ValueError):return {}

def opacity():
 try:return min(1,max(.75,float(preferences().get('opacity',.94))))
 except (TypeError,ValueError):return .94


def reload_widgets():
 import shutil,subprocess,tomllib
 backend=preferences().get('bar','noctalia')
 if backend=='noctalia' and shutil.which('noctalia'):
  data=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))
  manifest=data/'noctalia-plugins/updates/plugin.toml'
  try:
   plugin=tomllib.loads(manifest.read_text())['id']
   result=subprocess.run(['noctalia','config','export','full'],capture_output=True,text=True,timeout=10)
   enabled=tomllib.loads(result.stdout).get('plugins',{}).get('enabled',[]) if result.returncode==0 else []
   if plugin in enabled:
    stopped=subprocess.run(['noctalia','msg','plugins','disable',plugin],capture_output=True,timeout=10)
    if stopped.returncode==0:subprocess.run(['noctalia','msg','plugins','enable',plugin],capture_output=True,timeout=10)
  except (OSError,ValueError,KeyError,subprocess.TimeoutExpired):pass
 elif backend=='waybar' and shutil.which('pkill'):
  subprocess.run(['pkill','-u',str(os.getuid()),'-RTMIN+9','-x','waybar'])
 # Caelestia polls fresh data; restart that shell after editing its QML component.


def waybar_status(data,kind):
 import html
 if data.get('visible') is False:return {'text':'','tooltip':'','class':'hidden'}
 color=data.get('color',data.get('glyphColor','#'+palette()['accent']))
 icon='▣'
 tips='\n'.join(' · '.join(str(v) for v in row if v) for row in data.get('tips',[]))
 text=f'<span foreground="{color}">{icon}</span>'
 if data.get('displayMode')=='always':text+=' '+html.escape(data.get('text',''))
 return {'text':text,'tooltip':html.escape(data.get('text','')+'\n'+tips),
         'class':kind,'percentage':data.get('classProgress') or 0}

# KeepItNew settings. Names are stable across installers.
@lru_cache(maxsize=2)
def settings_fields(app):
 if app!=APP:raise ValueError('Unknown app')
 def field(key,label,choices,default,help):return (key,label,choices,default,help)
 yes=[(True,'On'),(False,'Off')]
 fields=[
  field('theme','Theme',[(name,name) for name in THEMES],'Nord','Applies to this app and its widget after Save.'),
  field('opacity','Window opacity',[(n/100,f'{n}%') for n in range(75,101)],.94,'Save updates opacity in app-launched Kitty windows. Older windows and other terminals need reopening from the widget or launcher.'),
  field(app+'_border','App borders',[(x,x.capitalize()) for x in ('single','double','ascii','none')],'single','Square terminal borders only; does not change desktop window decorations.'),
  field(app+'_border_color','Border color',[(x,label) for x,label in [('accent','Theme accent'),('purple','Secondary accent'),('dim','Muted')]],'accent','Colors always come from the selected theme.'),
  field(app+'_widget','Bar widget',yes,True,'Hide or show this app’s installed widgets. Hidden widgets still poll so they can reappear.'),
  field(app+'_widget_mode','Widget text',[(x,label) for x,label in [('hover','On hover'),('always','Always'),('icon','Icon only')]],'hover','Noctalia and Waybar text. Caelestia keeps details in its tooltip.'),
  field(app+'_animation','Widget animation',[(x,x.capitalize()) for x in ('gentle','fast','off')],'fast','Noctalia hover animation. Off reveals text immediately.'),
 ]
 fields += [
  field('updates_include_aur','Include AUR updates',yes,True,'Include AUR in checks and upgrades. Arch repository upgrades remain enabled.'),
  field('updates_flatpak_system','System Flatpak updates',yes,True,'Check and update system-wide Flatpak applications.'),
  field('updates_flatpak_user','User Flatpak updates',yes,True,'Check and update your per-user Flatpak applications.'),
  field('updates_aur_helper','Preferred AUR helper',[('auto','Auto · yay then paru'),('yay','yay preferred'),('paru','paru preferred')],'auto','Use the preferred installed helper, with fallback to the other. Does not install a helper.'),
  field('updates_cache_keep','Cached package versions',[(i,str(i)+' versions') for i in range(1,6)],2,'Versions retained by package-cache cleanup. Applies only when you select and run that cleanup category.'),
  field('checks_enabled','Automatic update checks',yes,True,'Enable or disable the installed user timer. This checks updates; it never installs them.'),
  field('check_minutes','Check interval',[(i,f'{i} min') for i in range(5,1441)],30,'Changes the user timer after Save. Manual checks remain available.'),
  field('auto_confirm','Automatic confirmations',yes,True,'Skip package-manager prompts after authentication. Does not start an update automatically.'),
  field('updates_reboot_hint','Reboot indicator',yes,True,'Show reboot recommendations in the widget; never reboot automatically.'),
  field('updates_cleanup_preset','Default cleanup preset',[(x,label) for x,label in [('l','Light'),('b','Balanced'),('d','Developer'),('f','Full'),('n','None')]],'l','Only preselects categories. Cleanup still requires clicking Clean.'),
 ]
 return fields


_OPTIONS_CACHE={}
def options(app):
 saved=preferences();theme=current();cached=_OPTIONS_CACHE.get(app)
 if cached and cached[0] is saved and cached[1]==theme:return dict(cached[2])
 result={}
 for key,_,choices,default,_ in settings_fields(app):
  value=theme if key=='theme' else saved.get(key,default)
  if key=='opacity' and type(value) is int:value=float(value)
  result[key]=value if any(type(value)==type(candidate) and value==candidate for candidate,_ in choices) else default
 _OPTIONS_CACHE[app]=(saved,theme,result)
 return dict(result)


def frame(app,values=None):
 values=options(app) if values is None else values
 return {'single':('┌','┐','└','┘','─','│'),'double':('╔','╗','╚','╝','═','║'),
         'ascii':('+','+','+','+','-','|'),'none':(' ',' ',' ',' ',' ',' ')}[values.get(app+'_border','single')]


def border_color(app):return palette()[options(app)[app+'_border_color']]


def widget_options(app):
 prefs=options(app)
 return {'visible':prefs[app+'_widget'],'displayMode':prefs[app+'_widget_mode'],
         'animation':{'off':1,'fast':.45,'gentle':.22}[prefs[app+'_animation']]}


def _write_bytes(path,content):
 path.parent.mkdir(parents=True,exist_ok=True);temporary=None
 try:
  with tempfile.NamedTemporaryFile('wb',dir=path.parent,delete=False) as file:
   temporary=Path(file.name);file.write(content)
  os.replace(temporary,path)
 finally:
  if temporary is not None:temporary.unlink(missing_ok=True)


def _write_json(path,data):
 _write_bytes(path,(json.dumps(data,indent=2)+'\n').encode())


def save_options(app,values):
 import fcntl,subprocess
 fields=settings_fields(app);valid={key:choices for key,_,choices,_,_ in fields}
 if set(values)!=set(valid):raise ValueError('Invalid settings fields')
 for key,value in values.items():
  if not any(type(value)==type(candidate) and value==candidate for candidate,_ in valid[key]):raise ValueError('Invalid '+key)
 path=SETTINGS.parent/'preferences.json';path.parent.mkdir(parents=True,exist_ok=True)
 with (path.parent/'settings.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  old=preferences().copy();merged=dict(old);merged.update({k:v for k,v in values.items() if k!='theme'})
  service_change=old.get('service_pending',False) or any(old.get(k,default)!=values[k] for k,default in [('checks_enabled',True),('check_minutes',30)])
  if service_change:merged['service_pending']=True
  theme_changed=values['theme']!=current();previous_theme=SETTINGS.read_bytes() if SETTINGS.exists() else None
  try:
   if theme_changed:save(values['theme'])
   _write_json(path,merged)
  except OSError:
   if theme_changed:
    if previous_theme is None:SETTINGS.unlink(missing_ok=True)
    else:_write_bytes(SETTINGS,previous_theme)
   raise
 opacity_note=apply_opacity(values['opacity']) if old.get('opacity',.94)!=values['opacity'] else ''
 if service_change:
  config=Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))
  unit=config/'systemd/user/system-update-check.timer'
  if not unit.exists() and not (Path('/usr/lib/systemd/user')/unit.name).exists():return 'Settings saved. Install KeepItNew’s background service to apply scheduling.'
  try:
   dropin=unit.parent/'system-update-check.timer.d/keepitnew.conf'
   _write_bytes(dropin,('[Timer]\nOnUnitActiveSec=\nOnUnitActiveSec='+str(values['check_minutes'])+'min\n').encode())
   commands=[['systemctl','--user','daemon-reload'],['systemctl','--user','enable' if values['checks_enabled'] else 'disable','--now',unit.name]]
   if values['checks_enabled']:commands.append(['systemctl','--user','restart',unit.name])
   for command in commands:
    result=subprocess.run(command,capture_output=True,text=True,timeout=15)
    if result.returncode:return 'Settings saved; service change failed: '+(result.stderr.strip() or 'systemctl error')[:120]
  except (OSError,subprocess.TimeoutExpired) as exc:return 'Settings saved; service change failed: '+str(exc)[:120]
  with (path.parent/'settings.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);merged=preferences().copy();merged['service_pending']=False;_write_json(path,merged)
 return 'Saved. '+opacity_note


def settings(app):
 """Interactive settings with explicit save and discard."""
 import curses,sys
 if not sys.stdin.isatty() or not sys.stdout.isatty():
  print('Open Settings in an interactive terminal.');return
 fields=settings_fields(app);name=APP_NAME
 def screen(win):
  draft=options(app);original=dict(draft);cursor=0;offset=0;notice=''
  curses.raw();curses.curs_set(0);win.keypad(True);curses.start_color();curses.use_default_colors()
  curses.mousemask(curses.ALL_MOUSE_EVENTS);curses.mouseinterval(0)
  def put(y,text,style=0):
   h,w=win.getmaxyx()
   if 0<=y<h-1:
    try:win.addnstr(y,2,text,max(0,w-4),style)
    except curses.error:pass
  def apply():
   nonlocal original,notice
   try:notice=save_options(app,draft);original=dict(draft)
   except (ValueError,OSError) as exc:notice='Not saved: '+str(exc)
  while True:
   curses_colors(curses,win,draft['theme']);win.erase();h,w=win.getmaxyx();menu_frame(curses,win,app,draft)
   if h<16 or w<48:
    put(1,'Resize to 48 columns × 16 rows. Esc returns.');win.refresh()
    if win.getch() in (27,3):return
    continue
   put(1,name.upper()+' / SETTINGS'+(' · unsaved' if draft!=original else ''),curses.color_pair(1)|curses.A_BOLD)
   tl,tr,bl,br,horiz,vert=frame(app)
   put(2,'Appearance · Widgets · Background services',curses.color_pair(5))
   put(3,'↑↓ Move · ←→ Adjust · Enter Options · Ctrl+S Save',curses.color_pair(1))
   count=max(1,h-13);offset=min(offset,cursor)
   if cursor>=offset+count:offset=cursor-count+1
   for i,(key,label,choices,_,_) in enumerate(fields[offset:offset+count],offset):
    value=next(label for value,label in choices if draft[key]==value)
    label_width=max(12,min(25,w//3))
    shown=label if len(label)<=label_width else label[:label_width-1]+'…'
    line=('› ' if i==cursor else '  ')+shown.ljust(label_width)+f'  ‹ {value} ›'
    put(4+i-offset,line.ljust(max(0,w-4)),curses.color_pair(2) if i==cursor else 0)
   import textwrap
   for line,text in enumerate(textwrap.wrap(fields[cursor][1]+': '+fields[cursor][4],max(1,w-4))[:3]):put(h-7+line,text,curses.color_pair(1))
   put(h-4,notice or 'Theme colors preview here. Save applies; Esc discards.')
   labels=[('save','[ Save ]'),('reset','[ Defaults ]'),('cancel','[ Back / discard ]')]
   width=sum(len(label) for _,label in labels)+4;left=max(2,(w-width)//2);hits=[]
   for action,label in labels:
    try:win.addnstr(h-2,left,label,max(0,w-left-1),curses.color_pair(1)|curses.A_BOLD)
    except curses.error:pass
    hits.append((left,left+len(label),action));left+=len(label)+2
   win.refresh();key=win.getch();action=None
   if key==curses.KEY_MOUSE:
    try:_,x,y,_,state=curses.getmouse()
    except curses.error:continue
    if state & curses.BUTTON4_PRESSED:key=curses.KEY_UP
    elif state & getattr(curses,'BUTTON5_PRESSED',0):key=curses.KEY_DOWN
    elif state & (curses.BUTTON1_PRESSED|curses.BUTTON1_CLICKED):
     if y==h-2:action=next((a for lo,hi,a in hits if lo<=x<hi),None)
     elif 4<=y<4+min(count,len(fields)-offset):cursor=offset+y-4;key=10
     else:continue
    else:continue
   if key in (27,3,ord('q')) or action=='cancel':return
   if key==19 or action=='save':apply();continue
   if key==ord('r') or action=='reset':
    draft={key:default for key,_,_,default,_ in fields};notice='Defaults selected. Nothing changes until Save.';continue
   if key in (curses.KEY_DOWN,9):cursor=(cursor+1)%len(fields);notice=''
   elif key in (curses.KEY_UP,curses.KEY_BTAB):cursor=(cursor-1)%len(fields);notice=''
   elif key in (curses.KEY_NPAGE,curses.KEY_PPAGE):cursor=max(0,min(len(fields)-1,cursor+(count if key==curses.KEY_NPAGE else -count)))
   elif key in (curses.KEY_RIGHT,curses.KEY_LEFT,10,13,32):
    field,_,choices,_,_=fields[cursor];values=[value for value,_ in choices]
    if key in (10,13) and len(choices)>2:
     draft[field]=select_option(curses,win,fields[cursor][1],choices,draft[field]);notice='';continue
    step=5 if field=='check_minutes' else 1
    draft[field]=values[(values.index(draft[field])+(-step if key==curses.KEY_LEFT else step))%len(values)];notice=''
 try:run_screen(screen)
 except KeyboardInterrupt:pass
