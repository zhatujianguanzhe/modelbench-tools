import os,sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from tkinter import filedialog
import win32api,win32con
from PIL import Image,ImageTk,ImageDraw,ImageColor
import webbrowser
import json,math,ctypes,pyperclip

ctypes.windll.shcore.SetProcessDpiAwareness(1)#1禁用,0默认


if getattr(sys, 'frozen', None):
    resource_path = sys._MEIPASS.replace(r'\\','/').replace('\\',r'\\')+'/resource/'
else:
    resource_path = os.path.dirname(__file__).replace(r'\\','/').replace('\\',r'\\')+'/resource/'

#pyfile_dir_path = os.path.dirname( os.path.abspath(__file__))+'/'

def set_dark_title_bar(window):
    """
    通过 Windows API 强制将 Tkinter 窗口标题栏设置为深色模式
    """
    window.update() # 确保窗口已经创建并获得了句柄
    
    # 获取窗口句柄 (HWND)
    # 在某些 Python 版本中需要使用 int() 转换
    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    except:
        hwnd = window.winfo_id()

    # DWMWA_USE_IMMERSIVE_DARK_MODE 属性在 Win10/Win11 中的代码
    # 不同的 Windows 版本可能需要尝试 19 或 20
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    
    # 设置为 1 表示开启深色模式，0 表示浅色模式
    value = ctypes.c_int(1)
    
    # 调用 dwmapi.dll
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, 
        DWMWA_USE_IMMERSIVE_DARK_MODE, 
        ctypes.byref(value), 
        ctypes.sizeof(value)
    )

    window.update_idletasks()
    




class LinkLabel(tk.Label):
    def __init__(self, master, url='',command=None,**kw):
        super().__init__(master,**kw)
        self.url = url
        self.command = command
        self.create_LinkLabel()
        self.clicked=False

    def add_underline(self,label_widget):
        """
        为给定的 Tkinter Label widget 添加下划线效果，而不改变其他字体属性。
        """
        # 获取当前 Label 的字体配置
        current_font = tkfont.Font(font=label_widget.cget("font"))

        # 创建一个新的字体对象，基于当前字体，并设置下划线为 True
        new_font = tkfont.Font(
            family=current_font["family"],
            size=current_font["size"],
            weight=current_font["weight"],
            slant=current_font["slant"],
            underline=True,  # 只将下划线设置为 True
            overstrike=current_font["overstrike"],)
        # 将新的字体应用到 Label
        label_widget.config(font=new_font)

    def create_LinkLabel(self):
        self.config(fg="#0000EE",cursor='hand2')
        self.add_underline(self)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.enter_label)
        self.bind("<Leave>", self.leave_label)

    def on_click(self, event):
        self.clicked=True
        if self.command is not None:
            self.config(fg='#0000EE')
            self.command()
        else:
            self.config(fg='#551a8b')
            webbrowser.open_new_tab(self.url)
    
    def enter_label(self,event):
        self.config(fg="#0056b3")

    def leave_label(self,event):
        if self.clicked==True:
            self.config(fg='#551a8b')
        else:
            self.config(fg='#0000EE')

class TipsLabel(tk.Label):
    def __init__(self, master,text_tipswindow='',insert_picture_path=None ,icon='question',text_color="SystemButtonText", **kw):
        super().__init__(master,**kw)
        self.master=master
        self.text_tipswindow=text_tipswindow
        self.insert_picture_path=insert_picture_path
        self.icon=icon
        self.text_color=text_color
        self.create_TipsLabel()

    def set_image(self, tk_label, img_path, img_size=None):
        img_open = Image.open(img_path)
        if img_size:
            max_width, max_height = img_size
            img_w, img_h = img_open.size
            scale = min(max_width / img_w, max_height / img_h, 1)
            img_open = img_open.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
        img = ImageTk.PhotoImage(img_open)
        tk_label.config(image=img)
        tk_label.image = img

    def create_TipsLabel(self):
        self.config(text='',anchor='center',bd=0,relief='flat',compound='top',highlightbackground='SystemButtonFace',)
        self.set_image(self, resource_path + self.icon + ".ico", img_size=(25,25))
        
        self.bind('<Enter>',self.reshow_TipsWindow)
        self.bind('<Leave>',self.destroy_TipsWindow)
        self.bind('<Motion>',self.show_TipsWindow)
        self.bind('<Button-1>',self.reshow_TipsWindow)


    def reshow_TipsWindow(self,event=None):
        self.destroy_TipsWindow()
        self.show_TipsWindow()
    def show_TipsWindow(self,event=None):
        try:
            if self.TipsWindow.winfo_class()=='Toplevel':
                return
        except: pass            
        self.TipsWindow=tk.Toplevel(self.master)
        self.TipsWindow.title('')
        self.TipsWindow.overrideredirect(1)
        self.TipsWindow.resizable(0,0)
        self.TipsWindow['bg']='System3DLight'
        self.TipsWindow['bd']=1
        self.TipsWindow['relief']='solid'
        self.TipsWindow.attributes('-topmost',True)
        
        label_text=tk.Label(self.TipsWindow,text=self.text_tipswindow,justify='left',anchor='nw',bg='System3DLight',fg=self.text_color)#,wraplength=200)
        label_text.pack(fill='x',expand=True,padx=5,pady=5)

        
        if self.insert_picture_path!=None:
            label_picture=tk.Label(self.TipsWindow,bg='System3DLight',compound='center',anchor='center')
            label_picture.pack(fill='x',expand=True,padx=5,pady=5)
            self.photo=ImageTk.PhotoImage(file=self.insert_picture_path)
            label_picture.config(image=self.photo)
            label_text["wraplength"]=self.photo.width()
        else:
            label_text["wraplength"]=250
        
        
        self.TipsWindow.update_idletasks()
        geometry_x=self.TipsWindow.winfo_pointerxy()[0]+5
        if geometry_x+self.TipsWindow.winfo_reqwidth()+5>self.master.winfo_screenwidth():
            geometry_x=self.TipsWindow.winfo_pointerxy()[0]-self.TipsWindow.winfo_reqwidth()-5
        if geometry_x<0:
            geometry_x=0
        geometry_y=self.TipsWindow.winfo_pointerxy()[1]+5


        geometry = f'+{geometry_x}+{geometry_y}'
        self.TipsWindow.geometry(geometry)

        self.TipsWindow.wait_window(self.TipsWindow)

    def destroy_TipsWindow(self,event=None):
        try:
            self.TipsWindow.destroy()
        except:
            pass

class LoadingLabel(tk.Label):
    def __init__(self, master, **kw):
        super().__init__(master,**kw)
        self.master=master
        self.Text_Count=0xE052
        self.config(bd=0,anchor='center')
        try:
            self['font']=('LOADING_SegoeUI-Semilight Semilight',26)
        except:
            pass
        self.after(0,self.Text_LOADING_Update)

    def Text_LOADING_Update(self):
        try:

            if self.Text_Count+1>0xE0D0:
                self.Text_Count=0xE052
            else:
                self.Text_Count+=1
            self['text']=chr(self.Text_Count)+'\n正在处理\n程序卡死为正常现象'

            self.after(15,self.Text_LOADING_Update)
        except:
            return




def set_image(tk_widget, img_file_name, img_size=[32,32]):
    img_open = Image.open(f"{resource_path}{img_file_name}")
    img_w, img_h = img_open.size
    scale = min(img_size[0] / img_w, img_size[1] / img_h, 1)
    img_open = img_open.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
    img = ImageTk.PhotoImage(img_open)
    tk_widget.config(image=img)
    tk_widget.image = img



def MessageBox(parent=None, text='', title='', icon='none',text_true='确定',text_false='取消', buttonmode=1, defaultfocus=1):
    # 辅助函数：更精确地计算文本高度（改进版）
    def calculate_text_height_with_font(text_content, wraplength_val, font_object):
        """
        根据文本内容、换行宽度和字体对象估算文本在 Tkinter Label 中所需的像素高度。
        确保返回的高度至少为 90 像素，并增加更多缓冲。
        """
        # 确保最小高度
        MIN_LABEL_HEIGHT = 90 # 确保标签至少有 90 像素高

        if not text_content:
            return MIN_LABEL_HEIGHT # 空文本也至少有 MIN_LABEL_HEIGHT 像素高

        lines = 0
        current_line_width = 0
        
        # Splitting by words and then by '\n' allows for better handling of both automatic and manual wraps
        # We will process each 'part' which is either a word or a segment after a manual newline.
        parts_with_newlines_handled = []
        for segment in text_content.split('\n'):
            words_in_segment = segment.split(' ')
            parts_with_newlines_handled.extend(words_in_segment)
            parts_with_newlines_handled.append('\n') # Mark a manual newline

        # Remove the last '\n' if the original text didn't end with one, to avoid an extra blank line.
        if text_content and not text_content.endswith('\n'):
            parts_with_newlines_handled.pop()

        for i, part in enumerate(parts_with_newlines_handled):
            if part == '\n':
                lines += 1
                current_line_width = 0
                continue # Move to the next part

            part_width = font_object.measure(part)
            
            # If adding this part exceeds wraplength AND it's not the very first part of a new line, wrap
            if current_line_width + part_width > wraplength_val and current_line_width != 0:
                lines += 1
                current_line_width = part_width
            else:
                current_line_width += part_width # Add current part's width
            
            # Add space for the gap between words, but only if it's not the last word in the line
            # This needs careful handling to not add extra space after the last word if it wraps.
            # Simple approach for now: add space after each word.
            if i < len(parts_with_newlines_handled) -1 and parts_with_newlines_handled[i+1] != '\n':
                current_line_width += font_object.measure(' ')


        # If there's any content left on the last line, count it
        if current_line_width > 0 or not text_content: # Ensure at least one line for non-empty text
            lines += 1

        # Ensure at least one line is counted for very short text
        if lines == 0:
            lines = 1
                
        line_height = font_object.metrics('linespace')

        # **重要修改：增加更多的缓冲像素**
        # 20-30 像素的缓冲通常是比较安全的，用于Label的默认padding和渲染微小误差
        BUFFER_PIXELS = 25
        
        # 确保返回的高度至少为 MIN_LABEL_HEIGHT 像素
        return max(MIN_LABEL_HEIGHT, int(lines * line_height) + BUFFER_PIXELS)

    def set_image(tk_label, img_path, img_size=None):
        img_open = Image.open(img_path)
        if img_size:
            max_width, max_height = img_size
            img_w, img_h = img_open.size
            scale = min(max_width / img_w, max_height / img_h, 1)
            img_open = img_open.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
        img = ImageTk.PhotoImage(img_open)
        tk_label.config(image=img)
        tk_label.image = img

    def close_Message_Box_window():
        if parent:
            parent.attributes('-disabled', 'false')
        Message_Box_window.destroy()
        if parent:
            parent.focus_set()

    def return_value(value):
        nonlocal rtn
        rtn = value
        close_Message_Box_window()

    def handle_key(event):
        focused = Message_Box_window.focus_get()
        if event.keysym == 'Escape':  # If ESC key is pressed, return None
            return_value(None)
        elif focused in (ok_button, None):
            return_value(True)
        elif focused == cancel_button:
            return_value(False)

    def update_button_focus(event=None):
        if buttonmode == 2:

            if Message_Box_window.focus_get() == cancel_button:
                ok_button['default'], cancel_button['default'] = 'normal', 'active'
            else:# Message_Box_window.focus_get() == ok_button:
                ok_button['default'], cancel_button['default'] = 'active', 'normal'
    # 初始化 rtn
    rtn = None

    # 窗口初始化
    Message_Box_window = tk.Toplevel(parent) if parent else tk.Tk()
    Message_Box_window.title(title)
    initial_window_width = 390
    initial_window_height = 170 # This is a placeholder, will be updated later
    
    Message_Box_window.geometry(f'{initial_window_width}x{initial_window_height}+'
                                f'{(Message_Box_window.winfo_screenwidth() - initial_window_width) // 2}+'
                                f'{(Message_Box_window.winfo_screenheight() - initial_window_height) // 2}')
    
    Message_Box_window.resizable(False, False)
    Message_Box_window.protocol("WM_DELETE_WINDOW", close_Message_Box_window)
    Message_Box_window.focus_set()

    if parent:
        parent.attributes('-disabled', 'true')
        Message_Box_window.wm_transient(parent)

    label_icon = tk.Label(Message_Box_window, anchor='center')
    label_icon.place(x=20, y=20, width=45, height=45)

    TEXT_LABEL_X = 80
    TEXT_LABEL_Y = 20
    TEXT_LABEL_WRAPLENGTH = 282

    text_text = tk.Label(Message_Box_window, wraplength=TEXT_LABEL_WRAPLENGTH, text=text, justify='left', anchor='nw',)
    
    # Get the actual font used by the Label for measurement
    # It's crucial to get the font AFTER the label is created
    temp_label_for_font_measure = tk.Label(Message_Box_window) # Create a temporary label to get the default font
    actual_font_for_measure = tkfont.Font(font=temp_label_for_font_measure.cget('font')) # Get the font object
    temp_label_for_font_measure.destroy() # Destroy the temporary label

    # Calculate the required text label height
    calculated_text_height = calculate_text_height_with_font(text_content=text, 
                                                             wraplength_val=TEXT_LABEL_WRAPLENGTH,
                                                             font_object=actual_font_for_measure)

    TEXT_LABEL_HEIGHT = calculated_text_height

    text_text.place(x=TEXT_LABEL_X, y=TEXT_LABEL_Y, width=290, height=TEXT_LABEL_HEIGHT)

    if icon != 'none':
        set_image(label_icon, f"{resource_path}/{icon}.ico", img_size=(45, 45))

    BUTTON_HEIGHT = 30
    BUTTON_TOP_MARGIN = 15 # 10/20均可  Space between text label bottom and button top
    
    buttons_y = TEXT_LABEL_Y + TEXT_LABEL_HEIGHT + BUTTON_TOP_MARGIN

    WINDOW_BOTTOM_MARGIN = 20 # Keep consistent with top margin
    new_window_height = buttons_y + BUTTON_HEIGHT + WINDOW_BOTTOM_MARGIN

    Message_Box_window.geometry(f'{initial_window_width}x{new_window_height}+'
                                f'{(Message_Box_window.winfo_screenwidth() - initial_window_width) // 2}+'
                                f'{(Message_Box_window.winfo_screenheight() - new_window_height) // 2}')

    if buttonmode == 1:
        Message_Box_window.bind('<Escape>', handle_key)
        Message_Box_window.bind('<Return>', handle_key)
        ok_button = ttk.Button(Message_Box_window, text=text_true, command=lambda: return_value(True), default='active')
        ok_button.place(x=290, y=buttons_y, width=80, height=30)
        ok_button.focus()
    elif buttonmode == 2:
        Message_Box_window.bind('<Escape>', lambda e: return_value(None))
        Message_Box_window.bind('<Return>', handle_key)

        #Var_dont_warn=tk.BooleanVar()
        #Var_dont_warn.set(True)
        #Checkbutton_dont_warn=ttk.Checkbutton(Message_Box_window,text='保持选择,不再弹出.',style='Warning.TCheckbutton',onvalue=True,offvalue=False,variable=Var_dont_warn)
        #Checkbutton_dont_warn.bind('<Return>',lambda e:Checkbutton_dont_warn.invoke())
        
        ok_button = ttk.Button(Message_Box_window, text=text_true, command=lambda: return_value(True), )
        ok_button.place(x=190, y=buttons_y, width=80, height=30)

        cancel_button = ttk.Button(Message_Box_window, text=text_false, command=lambda: return_value(False))
        cancel_button.place(x=290, y=buttons_y, width=80, height=30)

        ok_button.bind("<FocusIn>", update_button_focus)
        cancel_button.bind("<FocusIn>", update_button_focus)
        ok_button.bind("<FocusOut>", update_button_focus)
        cancel_button.bind("<FocusOut>", update_button_focus)

        (ok_button if defaultfocus == 1 else cancel_button).focus()
        (ok_button if defaultfocus == 1 else cancel_button)['default']='active'
    else:
        raise ValueError("buttonmode 只能为 1 或 2")



    beep_map = {
        'question': win32con.MB_ICONQUESTION, 
        'error': win32con.MB_ICONERROR, 
        'warning': win32con.MB_ICONWARNING,
        'info': win32con.MB_ICONINFORMATION, 
        'correct': win32con.MB_ICONINFORMATION,
        'none': 0
    }

    win32api.MessageBeep(beep_map.get(icon, 0))
    Message_Box_window.wm_iconbitmap(f"{resource_path}icon.ico")
    Message_Box_window.wait_window(Message_Box_window)
    return rtn

def InputBox(title='', text='', parent=None, default='', canspace=True, canempty=False):
    rt = None

    def calculate_label_width_with_font(text_content, font_object, min_width=80, buffer_pixels=20):
        """
        根据文本内容和字体对象估算标签所需的像素宽度，返回值至少为 min_width，并加 buffer。
        """
        if not text_content:
            return min_width
        # 计算每一行的宽度（考虑换行）
        lines = text_content.split('\n')
        max_line_width = max(font_object.measure(line) for line in lines)
        return max(min_width, max_line_width + buffer_pixels)
    def close_handler():
        if parent:
            parent.attributes('-disabled', 'false')
        Input_Box_Auto_window.destroy()
        if parent:
            parent.focus_set()

    def close_handler_cancel():
        nonlocal rt
        rt = None
        close_handler()

    def save():
        nonlocal rt
        rt = entry_filename.get().strip()

        if not canspace and ' ' in rt:
            win32api.MessageBeep()
            entry_filename.focus()
        elif canempty or rt:
            close_handler()
        else:
            win32api.MessageBeep()
            entry_filename.focus()

    def save_(event=None):
        focused = Input_Box_Auto_window.focus_get()
        if focused in (save_btn, None):
            save()
        elif focused == close_btn:
            close_handler_cancel()
        else:
            save()

    def update_button_focus(event=None):
        if Input_Box_Auto_window.focus_get() == save_btn:
            save_btn['default'], close_btn['default'] = 'active', 'normal'
        elif Input_Box_Auto_window.focus_get() == close_btn:
            save_btn['default'], close_btn['default'] = 'normal', 'active'

    # 创建窗口
    Input_Box_Auto_window = tk.Toplevel(parent) if parent else tk.Tk()
    Input_Box_Auto_window.title(title)
    Input_Box_Auto_window.geometry(f'420x120+{(Input_Box_Auto_window.winfo_screenwidth() - 420) // 2}+{(Input_Box_Auto_window.winfo_screenheight() - 120) // 2}')
    Input_Box_Auto_window.resizable(False, False)
    Input_Box_Auto_window.protocol("WM_DELETE_WINDOW", close_handler_cancel)
    Input_Box_Auto_window.bind('<Return>', save_)
    Input_Box_Auto_window.bind('<Escape>', lambda e: close_handler_cancel())

    if parent:
        parent.attributes('-disabled', 'true')
        Input_Box_Auto_window.wm_transient(parent)

    # UI 组件
   
    # 获取字体对象
    temp_label = tk.Label(Input_Box_Auto_window)
    actual_font = tkfont.Font(font=temp_label.cget('font'))
    temp_label.destroy()

    # 计算标签宽度
    LABEL_MIN_WIDTH = 80
    label_width = calculate_label_width_with_font(text, actual_font, min_width=LABEL_MIN_WIDTH, buffer_pixels=20)
    entry_width = 380 - label_width  # 总宽度420减去左右边距和标签宽度

    tk.Label(Input_Box_Auto_window, text=text, anchor="w").place(x=20, y=20, width=label_width, height=30)
    entry_filename = ttk.Entry(Input_Box_Auto_window, takefocus=True)
    entry_filename.place(x=20 + label_width, y=20, width=entry_width, height=30)
    entry_filename.insert(0, default)
    entry_filename.focus()

    save_btn = ttk.Button(Input_Box_Auto_window, text="确定", command=save, default='active')
    save_btn.place(x=220, y=70, width=80, height=30)

    close_btn = ttk.Button(Input_Box_Auto_window, text="取消", command=close_handler_cancel)
    close_btn.place(x=320, y=70, width=80, height=30)

    save_btn.bind("<FocusIn>", update_button_focus)
    save_btn.bind("<FocusOut>", update_button_focus)
    close_btn.bind("<FocusIn>", update_button_focus)
    close_btn.bind("<FocusOut>", update_button_focus)

    Input_Box_Auto_window.wm_iconbitmap(f"{resource_path}icon.ico")
    Input_Box_Auto_window.wait_window(Input_Box_Auto_window)

    return rt

def ComboInputBox(title='', text='', parent=None,default='',value=(''),state='readonly'):
    rt=None
    def calculate_label_width_with_font(text_content, font_object, min_width=80, buffer_pixels=20):
        """
        根据文本内容和字体对象估算标签所需的像素宽度，返回值至少为 min_width，并加 buffer。
        """
        if not text_content:
            return min_width
        # 计算每一行的宽度（考虑换行）
        lines = text_content.split('\n')
        max_line_width = max(font_object.measure(line) for line in lines)
        return max(min_width, max_line_width + buffer_pixels)
    def close_handler():
        if parent!=None:
            parent.attributes('-disabled', 'false')
        Input_ComboboxBox_window.destroy()
        if parent!=None:
            parent.focus_set()
    def close_handler_cancel_(nothing):
        close_handler_cancel()
    def close_handler_cancel():
        nonlocal rt
        rt=None
        close_handler()
    def save():
        nonlocal rt
        rt=entry_filename.get()
        if rt.replace(' ','')!='':
            close_handler()
            return 0
        else:
            win32api.MessageBeep()
            entry_filename.focus()
            return 0
    def save_(nothing):
        nonlocal rt
        try:
            if Input_ComboboxBox_window.focus_get()==save_btn:
                save()
            elif Input_ComboboxBox_window.focus_get()==close:
                close_handler_cancel()

            else:
                save()
        except:
            save()
    def focus_see_(nothing):
        if Input_ComboboxBox_window.focus_get()!=None:
            if Input_ComboboxBox_window.focus_get()==save_btn:
                close['default']='normal'
                save_btn['default']='active'
            elif Input_ComboboxBox_window.focus_get()==close:
                save_btn['default']='normal'
                close['default']='active'
            else:
                close['default']='normal'
                save_btn['default']='active'


    if parent!=None:
        parent.attributes('-disabled', 'true')
        Input_ComboboxBox_window=tk.Toplevel(parent)
        Input_ComboboxBox_window.wm_transient(parent)
    else:
        Input_ComboboxBox_window=tk.Tk()
    Input_ComboboxBox_window.title(str(title))
    width=420
    height=120

    screenwidth = Input_ComboboxBox_window.winfo_screenwidth()
    screenheight = Input_ComboboxBox_window.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Input_ComboboxBox_window.geometry(geometry)
    Input_ComboboxBox_window.resizable(width=False, height=False)
    Input_ComboboxBox_window.bind('<Return>',save_)
    Input_ComboboxBox_window.focus_set()
    Input_ComboboxBox_window.protocol("WM_DELETE_WINDOW", close_handler_cancel)
    Input_ComboboxBox_window.bind('<Escape>',close_handler_cancel_)
    

    '''label_filename = tk.Label(Input_ComboboxBox_window,text=str(text),anchor="w")
    label_filename.place(x=20, y=20, width=80, height=30)'''

    Var_value=tk.StringVar()
    Var_value.set(str(default))
    '''entry_filename = ttk.Combobox(Input_ComboboxBox_window,values=value,textvariable=Var_value,state=state)
    entry_filename.place(x=100, y=20, width=300, height=30)
    entry_filename.focus()'''

    temp_label = tk.Label(Input_ComboboxBox_window)
    actual_font = tkfont.Font(font=temp_label.cget('font'))
    temp_label.destroy()

    # 计算标签宽度
    LABEL_MIN_WIDTH = 80
    label_width = calculate_label_width_with_font(text, actual_font, min_width=LABEL_MIN_WIDTH, buffer_pixels=20)
    entry_width = 380 - label_width  # 总宽度420减去左右边距和标签宽度

    tk.Label(Input_ComboboxBox_window, text=text, anchor="w").place(x=20, y=20, width=label_width, height=30)
    entry_filename = ttk.Combobox(Input_ComboboxBox_window,values=value,textvariable=Var_value,state=state)
    entry_filename.place(x=20 + label_width, y=20, width=entry_width, height=30)
    entry_filename.focus_set()

    save_btn= ttk.Button(Input_ComboboxBox_window, text="确定",command=save,default='active')
    save_btn.place(x=220, y=70, width=80, height=30)

    close = ttk.Button(Input_ComboboxBox_window, text="取消", command=close_handler_cancel)
    close.place(x=320, y=70, width=80, height=30)
    
    save_btn.bind("<FocusIn>", focus_see_)
    save_btn.bind("<FocusOut>", focus_see_)
    close.bind("<FocusIn>", focus_see_)
    close.bind("<FocusOut>", focus_see_)
    
    
    Input_ComboboxBox_window.wm_iconbitmap(f'{resource_path}icon.ico')
    Input_ComboboxBox_window.wait_window(Input_ComboboxBox_window)

    return rt




BACKUP_LANGUAGES={
  'ZH_CN':{
    "Modelbench-Tools          老桃万岁制作": "Modelbench-Tools          老桃万岁制作",
    "语言": "语言",
    "Modelbench工具集": "Modelbench工具集",
    "Blockbench工具集": "Blockbench工具集",
    "颜色工具集": "颜色工具集",
    "重置贴图纹理比例到1": "重置贴图纹理比例到1",
    "贴图合并": "贴图合并",
    "UV分离与整理": "UV分离与整理",
    "重命名红色重名组件": "重命名红色重名组件",
    "UV逐面转箱式": "UV逐面转箱式",
    "多行颜色数值转像素图像": "多行颜色数值转像素图像",
    "确定": "确定",
    "取消": "取消",
    "...": "...",
    "原mimodel文件路径:": "原mimodel文件路径:",
    "原贴图的纹理比例:": "原贴图的纹理比例:",
    "新mimodel文件路径:": "新mimodel文件路径:",
    "新贴图文件路径:": "新贴图文件路径:",
    "原贴图文件路径:": "原贴图文件路径:",
    "新贴图宽:": "新贴图宽:",
    "新贴图高:": "新贴图高:",
    "按下回车键确定": "按下回车键确定",
    "Github项目页": "Github项目页",
    "Discord伺服器": "Discord伺服器",
    "版本:1.1.4          版权:copyright © 2025-2030 炸图监管者": "版本:1.1.4          版权:copyright © 2025-2030 炸图监管者",
    "错误": "错误",
    "信息": "信息",
    "警告": "警告",
    "未选择原mimodel文件.": "未选择原mimodel文件.",
    "未选择原贴图文件.": "未选择原贴图文件.",
    "未选择新mimodel文件.": "未选择新mimodel文件.",
    "未选择新贴图文件.": "未选择新贴图文件.",
    "原mimodel文件不存在.": "原mimodel文件不存在.",
    "原贴图文件不存在.": "原贴图文件不存在.",
    "新mimodel型文件已存在.": "新mimodel型文件已存在.",
    "新贴图文件已存在.": "新贴图文件已存在.",
    "链接贴图": "链接贴图",
    "文件:": "文件:",
    "链接的材质文件不存在.": "链接的材质文件不存在.",
    "处理完成.": "处理完成.",
    "处理文件时发生错误.\n详细信息: ": "处理文件时发生错误.\n详细信息: ",
    "保持选择,不再弹出.": "保持选择,不再弹出.",
    "在不改变模型内容的前提下,将mimodel中某个贴图的纹理比例(如下如所示)重置为1,并相应调整UV坐标和方块尺寸,最终生成一个处理好的模型文件(不会生成贴图文件!).":"在不改变模型内容的前提下,将mimodel中某个贴图的纹理比例(如下如所示)重置为1,并相应调整UV坐标和方块尺寸,最终生成一个处理好的模型文件(不会生成贴图文件!).",
    "●一次只能对一张贴图进行处理,可对生成后的模型文件进行再次处理.": "●一次只能对一张贴图进行处理,可对生成后的模型文件进行再次处理.",
    "将一个模型中的所有贴图合并为一个贴图,最终生成一个模型文件和一个贴图文件.": "将一个模型中的所有贴图合并为一个贴图,最终生成一个模型文件和一个贴图文件.",
    "●贴图合并时需手动排布,并按下回车键确定.": "●贴图合并时需手动排布,并按下回车键确定.",
    "将杂乱无章的UV整理得井然有序(这在接单中比较有用,虽然没什么实际用处),最终生成一个模型文件和一个贴图文件.": "将杂乱无章的UV整理得井然有序(这在接单中比较有用,虽然没什么实际用处),最终生成一个模型文件和一个贴图文件.",
    "●仅接受纹理比例为1的单一贴图的模型文件.\n●不支持\"混合材质\"项.\n●新贴图宽高要合理,否则程序运行出错或缓慢.\n●建议保持勾选底部两个复选框,必须勾选右边的复选框,否则贴图在ModelBench中设定的透明度会失效(ModelBench不支持透明度纹理,亲测!).": "●仅接受纹理比例为1的单一贴图的模型文件.\n●不支持\"混合材质\"项.\n●新贴图宽高要合理,否则程序运行出错或缓慢.\n●建议保持勾选底部两个复选框,必须勾选右边的复选框,否则贴图在ModelBench中设定的透明度会失效(ModelBench不支持透明度纹理,亲测!).",
    "将ModelBench中红色的重名部件全部改名为不重名的名称,保证ModelBench与Mine-imator的名称一致性.": "将ModelBench中红色的重名部件全部改名为不重名的名称,保证ModelBench与Mine-imator的名称一致性.",
    "将多行颜色的十六进制值绘制为一个像素线条并作为文件生成.": "将多行颜色的十六进制值绘制为一个像素线条并作为文件生成.",
    "填写Modelbench中如下图所示的位置的数字(不是这张图上的!!!).": "填写Modelbench中如下图所示的位置的数字(不是这张图上的!!!).",
    "未选择原bb模型文件.": "未选择原bb模型文件.",
    "原bb模型文件不存在.": "原bb模型文件不存在.",
    "新bb模型文件已存在.": "新bb模型文件已存在.",
    "新贴图宽输入错误.": "新贴图宽输入错误.",
    "新贴图高输入错误.": "新贴图高输入错误.",
    "原bb模型文件路径:": "原bb模型文件路径:",
    "新bb模型文件路径:": "新bb模型文件路径:",
    "保留MB颜色属性": "保留MB颜色属性",
    "保留MB透明度属性(推荐)": "保留MB透明度属性(推荐)",
    "仅支持单贴图,多贴图需完整UV合并工具完成.不支持\"混合材质\"项.": "仅支持单贴图,多贴图需完整UV合并工具完成.不支持\"混合材质\"项.",
    "必须使用通用模型进行转换;不支持网格对象;逐面贴图不能拉伸.": "必须使用通用模型进行转换;不支持网格对象;逐面贴图不能拉伸.",
    "方块 {} 的 {} 面出现拉伸错误,会导致贴图错误.": "方块 {} 的 {} 面出现拉伸错误,会导致贴图错误.",
    "忽略": "忽略",
    "终止": "终止",
    "原bb模型文件不是逐面UV.": "原bb模型文件不是逐面UV.",
    "原bb模型文件读取或解析失败.\n详细信息: ": "原bb模型文件读取或解析失败.\n详细信息: " 
    },
}
LANGUAGES={}
#LANGUAGES=BACKUP_LANGUAGES
CURRENT_LANGUAGE='ZH_CN'#先做好初始化
LANGUAGES_CODES=[]

def refresh_LANGUAGE_CODES():
    global LANGUAGES_CODES,CURRENT_LANGUAGE,LANGUAGES
    LANGUAGES_CODES=[]
    """LANGUAGES_CODES = [
    os.path.splitext(f)[0] 
    for f in os.listdir(f"{pyfile_dir_path}languages/") 
    if os.path.isfile(os.path.join(f"{pyfile_dir_path}languages/", f))
    ]"""


    # 2. 使用 for 循环遍历每一项
    for f in os.listdir("languages/"):
        # 3. 拼接完整路径
        full_path = os.path.join("languages/", f)
        
        # 4. 使用 if 嵌套判断是否为文件
        if os.path.isfile(full_path):
            # 5. 如果是文件，则添加到列表中
            if os.path.splitext(f)[1] == '.json':
                LANGUAGES_CODES.append(os.path.splitext(f)[0])
    LANGUAGES_CODES.remove('language_settings')

    if CURRENT_LANGUAGE not in LANGUAGES_CODES:
        CURRENT_LANGUAGE='ZH_CN'

try:
    if not os.path.exists("languages/ZH_CN.json"):
        with open ("languages/ZH_CN.json", 'w', encoding='utf-8') as f:
            json.dump(BACKUP_LANGUAGES['ZH_CN'], f, ensure_ascii=False, indent=4)
    
    #if not os.path.exists(f"{pyfile_dir_path}languages/EN_US.json"):
    #    with open (f"{pyfile_dir_path}languages/EN_US.json", 'w', encoding='utf-8') as f:
    #        json.dump(BACKUP_LANGUAGES['EN_US'], f, ensure_ascii=False, indent=4)

    if os.path.exists("languages/language_settings.json"):
        with open("languages/language_settings.json", 'r', encoding='utf-8') as f:
            language_data=json.load(f)
        CURRENT_LANGUAGE=language_data.get("current_language","ZH_CN")
    else:
        with open("languages/language_settings.json", 'w', encoding='utf-8') as f:
            json.dump({"current_language": "ZH_CN"}, f, ensure_ascii=False, indent=4)

    refresh_LANGUAGE_CODES()

    for code in LANGUAGES_CODES:
        with open(f"languages/{code}.json", 'r', encoding='utf-8') as f:
            LANGUAGES[code]=json.load(f)
    
except Exception as e:
    MessageBox(parent=None,text=f"加载语言文件出错,将使用默认语言包.\n详细信息: {e}",title='错误',icon="error")
    LANGUAGES=BACKUP_LANGUAGES


#新的覆盖默认的


def lang(text):
    global CURRENT_LANGUAGE,LANGUAGES
    return LANGUAGES[CURRENT_LANGUAGE].get(text,text)


def MimodelResetTextureScale():
    global MimodelResetTextureScale_all_texture_dict
    MimodelResetTextureScale_all_texture_dict={}

    def traverse_parts_shapes_set_temp_texture_key_and_statistic_textures(data, parent_texture=None):
        # 本层贴图（如果当前节点有）
        current_texture = data.get('texture', parent_texture)
        if current_texture:
            MimodelResetTextureScale_all_texture_dict.setdefault(current_texture, None)

        # 处理 shapes
        if "shapes" in data:
            shapes = data["shapes"]
            for shape in shapes:
                # shape 自己有 texture → 必须记录！
                if "texture" in shape:
                    tex = shape["texture"]
                    MimodelResetTextureScale_all_texture_dict.setdefault(tex, None)
                    shape["absolute_texture"] = tex

                else:
                    # shape 不含 texture → 继承
                    shape["absolute_texture"] = current_texture
        # 处理 parts
        if "parts" in data:
            for subpart in data["parts"]:
                # subpart 自己有 texture → 必须记录！
                if "texture" in subpart:
                    tex = subpart["texture"]
                    MimodelResetTextureScale_all_texture_dict.setdefault(tex, None)
                    subpart["absolute_texture"] = tex
                    traverse_parts_shapes_set_temp_texture_key_and_statistic_textures(subpart, parent_texture=tex)
                else:
                    # 没 texture → 继承
                    subpart["absolute_texture"] = current_texture
                    traverse_parts_shapes_set_temp_texture_key_and_statistic_textures(subpart, parent_texture=current_texture)

    def traverse_shapes_edit_texturescale(part,target_texture='',n=1):
        global MimodelResetTextureScale_all_texture_dict
        if 'shapes' in part:
            shapes = part['shapes']
            for i, shape in enumerate(shapes):
                if shape['absolute_texture'] == target_texture:
                    if 'texture_scale' in shape:
                        shape['texture_scale'] = 1
                    shape['uv']=[shape['uv'][0]*n,shape['uv'][1]*n]
                    shape['from']=[shape['from'][0]*n,shape['from'][1]*n,shape['from'][2]*n]
                    #int(xxxx*100000)/100000
                    #size_new_x=abs(shape['to'][0]-shape['from'][0])*n
                    #size_new_y=abs(shape['to'][1]-shape['from'][1])*n
                    #size_new_z=abs(shape['to'][2]-shape['from'][2])*n
                    shape['to']=[shape['to'][0]*2,shape['to'][1]*2,shape['to'][2]*2]
                    if 'scale' not in shape:
                        shape['scale']=[1,1,1]
                    shape['scale']=[int(shape['scale'][0]/n*100000)/100000,
                                    int(shape['scale'][1]/n*100000)/100000,
                                    int(shape['scale'][2]/n*100000)/100000] 
                    shapes[i] = shape #写回数据,必须

        if 'parts' in part:
            for subpart in part['parts']:
                traverse_shapes_edit_texturescale(subpart,target_texture=target_texture,n=n)

    def run_MimodelResetTextureScale(event=None):
        global MimodelResetTextureScale_all_texture_dict

        original_mimodel_file=Entry_original_mimodel_file.get().strip().replace('\\','/')
        new_mimodel_file=Entry_new_mimodel_file.get().strip().replace('\\','/')
        if original_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelResetTextureScale,title='错误',text='未选择原mimodel文件.',icon='error');Entry_original_mimodel_file.focus_set();return
        if new_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelResetTextureScale,title='错误',text='未选择新mimodel文件.',icon='error');Entry_new_mimodel_file.focus_set();return
        if not os.path.exists(original_mimodel_file): MessageBox(parent=Window_MimodelResetTextureScale,title='错误',text='原mimodel文件不存在.',icon='error');Entry_original_mimodel_file.focus_set();return
        if os.path.exists(new_mimodel_file): MessageBox(parent=Window_MimodelResetTextureScale,title='错误',text='新mimodel型文件已存在.',icon='error');Entry_new_mimodel_file.focus_set();return
        original_scale=Entry_original_texture_scale.get()
        try: 
            if original_scale.replace(' ','')=='':
                raise ValueError
            original_scale=int(original_scale)
            if original_scale<1:
                raise ValueError#('原始贴图比例不能小于1.')
        except: 
            MessageBox(parent=Window_MimodelResetTextureScale,title='错误',text='输入的原始贴图比例不是有效值错误.',icon='error')
            return

        try:
            for child in Window_MimodelResetTextureScale.winfo_children():
                if child.winfo_class()=='TButton':
                    child.config(state='disabled')
                elif child.winfo_class() in ['TCombobox','TEntry','TSpinbox']:
                    child.config(state='readonly')
            loading_label=LoadingLabel(Window_MimodelResetTextureScale,)
            loading_label.pack(fill='both',expand=True)
            Window_MimodelResetTextureScale.update()


            with open(original_mimodel_file,'r',encoding='utf-8') as f:
                data_original_mimodel=json.loads(f.read())

            traverse_parts_shapes_set_temp_texture_key_and_statistic_textures(data_original_mimodel)

            original_texture=ComboInputBox(parent=Window_MimodelResetTextureScale,title='选择要重置贴图缩放比例的贴图',text='贴图:',value=list(MimodelResetTextureScale_all_texture_dict.keys()))
            if original_texture==None:return

            traverse_shapes_edit_texturescale(data_original_mimodel,target_texture=original_texture,n=original_scale)

            with open(new_mimodel_file,'w',encoding='utf-8') as f:
                f.write(json.dumps(data_original_mimodel,indent=4,ensure_ascii=False))
            
            MessageBox(parent=Window_MimodelResetTextureScale,title='信息',text='处理完成.',icon='info')

        except Exception as e:
            MessageBox(parent=Window_MimodelResetTextureScale,title='错误',text=f'处理文件时发生错误.\n详细信息: {e}',icon='error')
            return
        finally:
            for child in Window_MimodelResetTextureScale.winfo_children():
                if child.winfo_class() in ( 'TEntry', 'TButton' , 'TSpinbox'):
                    child.config(state='normal')
            loading_label.destroy()
            Window_MimodelResetTextureScale.update()

    def close_Window_MimodelResetTextureScale(event=None):
        Window_MimodelResetTextureScale.destroy()
    Window_MimodelResetTextureScale=tk.Toplevel(root)
    Window_MimodelResetTextureScale.title('mimodel贴图缩放比例重置')
    width=510
    height=220
    screenwidth = Window_MimodelResetTextureScale.winfo_screenwidth()
    screenheight = Window_MimodelResetTextureScale.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Window_MimodelResetTextureScale.geometry(geometry)
    Window_MimodelResetTextureScale.resizable(0,0)
    Window_MimodelResetTextureScale.bind('<Escape>',close_Window_MimodelResetTextureScale)
    Window_MimodelResetTextureScale.focus()

    tk.Label(Window_MimodelResetTextureScale,text='原mimodel文件路径:',anchor='w').place(x=20,y=20,width=170,height=30)
    Entry_original_mimodel_file=ttk.Entry(Window_MimodelResetTextureScale,)
    Entry_original_mimodel_file.place(x=200,y=20,width=230,height=30)
    def browse_original_mimodel_file():
        file_path = filedialog.askopenfilename(parent=Window_MimodelResetTextureScale,filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_original_mimodel_file.delete(0, 'end')
            Entry_original_mimodel_file.insert(0, file_path)
    Button_browse_original_mimodel_file=ttk.Button(Window_MimodelResetTextureScale,text='...',command=browse_original_mimodel_file)
    Button_browse_original_mimodel_file.place(x=450,y=20,width=40,height=30)


    tk.Label(Window_MimodelResetTextureScale,text='原贴图的纹理比例:',anchor='w').place(x=20,y=70,width=170,height=30)
    Entry_original_texture_scale=ttk.Spinbox(Window_MimodelResetTextureScale,increment=1,from_=1,to=float('inf'))
    Entry_original_texture_scale.place(x=200,y=70,width=230,height=30)

    TipsLabel(Window_MimodelResetTextureScale,text_tipswindow='填写Modelbench中如下图所示的位置的数字(不是这张图上的!!!).',insert_picture_path=f'{resource_path}tips1.png',icon='question').place(x=450,y=70,width=40,height=30)


    tk.Label(Window_MimodelResetTextureScale,text='新mimodel文件路径:',anchor='w').place(x=20,y=120,width=170,height=30)
    Entry_new_mimodel_file=ttk.Entry(Window_MimodelResetTextureScale,)
    Entry_new_mimodel_file.place(x=200,y=120,width=230,height=30)
    
    def browse_new_mimodel_file():
        file_path = filedialog.asksaveasfilename(parent=Window_MimodelResetTextureScale,defaultextension='.mimodel',filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_mimodel_file.delete(0, 'end')
            Entry_new_mimodel_file.insert(0, file_path)
    Button_browse_new_mimodel_file=ttk.Button(Window_MimodelResetTextureScale,text='...',command=browse_new_mimodel_file)
    Button_browse_new_mimodel_file.place(x=450,y=120,width=40,height=30)


    Window_MimodelResetTextureScale.bind('<Return>',run_MimodelResetTextureScale)
    Button_start=ttk.Button(Window_MimodelResetTextureScale,text='确定',default='active',command=run_MimodelResetTextureScale)
    Button_start.place(x=410,y=170,width=80,height=30)

    Window_MimodelResetTextureScale.iconbitmap(f"{resource_path}icon.ico")
    Window_MimodelResetTextureScale.wait_window(Window_MimodelResetTextureScale)

def MimodelTextureMmerge():
    global all_texture_dict
    all_texture_dict={}

    def traverse_parts_shapes_set_temp_texture_key(data, parent_texture=None):
        global all_texture_dict
        
        # 本层贴图（如果当前节点有）
        current_texture = data.get('texture', parent_texture)
        if current_texture:
            all_texture_dict.setdefault(current_texture, None)

        # 处理 shapes
        if "shapes" in data:
            shapes = data["shapes"]
            for shape in shapes:
                # shape 自己有 texture → 必须记录！
                if "texture" in shape:
                    tex = shape["texture"]
                    all_texture_dict.setdefault(tex, None)
                else:
                    # shape 不含 texture → 继承
                    shape["temp_texture"] = current_texture

                # 不修改其他字段

        # 处理 parts
        if "parts" in data:
            for subpart in data["parts"]:
                # subpart 自己有 texture → 必须记录！
                if "texture" in subpart:
                    tex = subpart["texture"]
                    all_texture_dict.setdefault(tex, None)
                    traverse_parts_shapes_set_temp_texture_key(subpart, parent_texture=tex)
                else:
                    # 没 texture → 继承
                    subpart["temp_texture"] = current_texture
                    traverse_parts_shapes_set_temp_texture_key(subpart, parent_texture=current_texture)

    def traverse_shapes_set_uv_offset(part):
        global all_texture_offset_dict, new_texture_img, all_texture_dict,all_texture_offset_dict
        if 'shapes' in part:
            shapes = part['shapes']
            for i, shape in enumerate(shapes):
                texture_name = shape['temp_texture'] if 'texture' not in shape else shape['texture']
                offset = all_texture_offset_dict[texture_name]
                shape['uv'] = [shape['uv'][0] + offset[0],  # x轴偏移
                            shape['uv'][1] + offset[1]]   # y轴偏移
                shapes[i] = shape #写回数据,必须

        if 'parts' in part:
            for subpart in part['parts']:
                traverse_shapes_set_uv_offset(subpart)

    def traverse_parts_delete_texture_key(part):
        if 'shapes' in part:
            shapes = part['shapes']
            for i, shape in enumerate(shapes):
                if 'texture' in shape:
                    del shape['texture']
                if 'temp_texture' in shape:
                    del shape['temp_texture']
                shapes[i] = shape  # 写回原数据
        # 如果有子 parts，递归处理
        if 'parts' in part:
            parts=part['parts']
            for i, subpart in enumerate(parts):
                if 'texture' in subpart:
                    del subpart['texture']
                parts[i] = subpart  # 写回原数据
                traverse_parts_delete_texture_key(subpart)

    def run_DragDropTextrue():

        global DRAGGABLE_WIDGETS,all_texture_dict
        err=None
        # 全局变量：存储所有可拖动的控件
        # 这允许我们在拖动时检查当前控件与列表中其他所有控件的碰撞
        DRAGGABLE_WIDGETS = []

        def get_widget_bounds(widget):
            """
            获取控件相对于其父控件 (Canvas_pictures) 的边界信息。
            返回 (x, y, width, height)
            """
            # 确保控件已经渲染完成，否则 winfo_width/height 可能为 1
            widget.update_idletasks()
            
            x = widget.winfo_x()
            y = widget.winfo_y()
            w = widget.winfo_width()
            h = widget.winfo_height()
            return x, y, w, h

        def check_overlap(rect1, rect2):
            """
            检查两个矩形 (AABB) 是否重叠。
            矩形格式: (x, y, width, height)
            """
            x1, y1, w1, h1 = rect1
            x2, y2, w2, h2 = rect2

            # 如果满足以下任一条件，则不重叠：
            if x1 >= x2 + w2 :
                return False
            if x2 >= x1 + w1 :
                return False
            if y1 >= y2 + h2 :
                return False
            if y2 >= y1 + h1 :
                return False
            # 否则，重叠
            return True

        # ------------------ 新增：Swept AABB (连续碰撞检测) ------------------
        def swept_aabb(moving_rect, dx, dy, static_rect):
            """
            Swept AABB：检测移动矩形在做平移 (dx,dy) 期间与静态矩形是否相撞。
            moving_rect/static_rect 格式: (x, y, w, h)
            返回 (collision_time, normal_x, normal_y)
            - collision_time: 首次相撞时相对比例 t in [0,1], 若无碰撞返回 None
            - normal_x, normal_y: 碰撞法线（用于滑动判断）
            算法来源：经典 swept AABB（求 entry/exit time）
            """
            mx, my, mw, mh = moving_rect
            sx, sy, sw, sh = static_rect

            # 如果起始时已重叠，则认为在 t=0 就发生碰撞 —— 直接返回 0（视为碰撞）
            if check_overlap(moving_rect, static_rect):
                return 0.0, 0.0, 0.0

            # 边界相对移动量（将静态看作移动的反向）
            # 计算在每个轴上的 entry/exit 时间（以 t ∈ R，真实移动等于 t*(dx,dy)，其中 t∈[0,1] 为整段移动）
            if dx == 0:
                x_entry = -math.inf
                x_exit = math.inf
            else:
                if dx > 0:
                    x_entry = (sx - (mx + mw)) / dx
                    x_exit  = ((sx + sw) - mx) / dx
                else:
                    x_entry = ((sx + sw) - mx) / dx
                    x_exit  = (sx - (mx + mw)) / dx

            if dy == 0:
                y_entry = -math.inf
                y_exit = math.inf
            else:
                if dy > 0:
                    y_entry = (sy - (my + mh)) / dy
                    y_exit  = ((sy + sh) - my) / dy
                else:
                    y_entry = ((sy + sh) - my) / dy
                    y_exit  = (sy - (my + mh)) / dy

            entry_time = max(x_entry, y_entry)
            exit_time  = min(x_exit, y_exit)

            # 无碰撞条件
            if entry_time > exit_time:
                return None
            if entry_time < 0 or entry_time > 1:
                return None

            # 确定法线（哪个轴先到达为碰撞轴）
            normal_x = 0.0
            normal_y = 0.0
            if x_entry > y_entry:
                # x 轴先到达
                normal_x = -1.0 if dx > 0 else 1.0
                normal_y = 0.0
            else:
                normal_y = -1.0 if dy > 0 else 1.0
                normal_x = 0.0

            return entry_time, normal_x, normal_y

        def find_earliest_collision(widget, dx, dy):
            """
            对所有其他控件进行 swept 检测，返回 earliest collision 信息：
            (earliest_t, collision_widget, normal_x, normal_y)
            若无碰撞，返回 (None, None, 0, 0)
            """
            mx, my, mw, mh = get_widget_bounds(widget)
            earliest_t = None
            hit_widget = None
            hit_nx, hit_ny = 0.0, 0.0

            for other in DRAGGABLE_WIDGETS:
                if other is widget:
                    continue
                sx, sy, sw, sh = get_widget_bounds(other)
                res = swept_aabb((mx, my, mw, mh), dx, dy, (sx, sy, sw, sh))
                if res is not None:
                    t, nx, ny = res
                    # 取最早的正时间碰撞
                    if t is not None and 0.0 <= t <= 1.0:
                        if earliest_t is None or t < earliest_t:
                            earliest_t = t
                            hit_widget = other
                            hit_nx, hit_ny = nx, ny

            return earliest_t, hit_widget, hit_nx, hit_ny

        def is_overlapping_any_other_widget(current_widget, proposed_x, proposed_y):
            """
            检查当前控件在建议的新位置是否与任何其他控件重叠。
            """
            # 待检测控件的新边界
            current_w = current_widget.winfo_width()
            current_h = current_widget.winfo_height()
            proposed_rect = (proposed_x, proposed_y, current_w, current_h)
            
            for other_widget in DRAGGABLE_WIDGETS:
                # 跳过与自身比较
                if other_widget is current_widget:
                    continue
                    
                # 获取其他控件的当前边界
                other_rect = get_widget_bounds(other_widget)
                
                # 如果任一控件重叠，则返回 True
                if check_overlap(proposed_rect, other_rect):
                    return True
            return False

        def mousedown(event):
            """
            记录开始拖动时的鼠标位置
            """
            widget = event.widget
            # 记录鼠标在控件内部的相对坐标
            widget.startx = event.x
            widget.starty = event.y

            Label_Downtabel['text']=f'      ( {widget.winfo_x()} , {widget.winfo_y()} )      ( {widget.winfo_x()+widget.winfo_x()+widget.winfo_width()-1} , {widget.winfo_y()+widget.winfo_height()-1} )      [ {widget.winfo_width()} , {widget.winfo_height()} ]'           


        def drag(event):
            """
            计算新位置，使用 Swept AABB 实现连续碰撞检测 (CCD)，并保留滑动效果。
            """
            widget = event.widget

            # 计算鼠标相对于起始点的位移 (dx, dy)
            dx = event.x - widget.startx
            dy = event.y - widget.starty
            
            current_x = widget.winfo_x()
            current_y = widget.winfo_y()
            
            # 1. 计算建议的新坐标 (pro_x, pro_y)
            proposed_x = int(current_x + dx)
            proposed_y = int(current_y + dy)
        
            # --- 2. 边界限制 (应用到 proposed 坐标) ---
            
            # X 轴边界检查
            if proposed_x < 0:
                proposed_x = 0

            # Y 轴边界检查
            if proposed_y < 0:
                proposed_y = 0

            # 目标整体移动向量
            move_dx = proposed_x - current_x
            move_dy = proposed_y - current_y

            # 如果移动很小，直接尝试原先的分轴滑动（保持兼容）
            if move_dx == 0 and move_dy == 0:
                return

            # --- CCD 主流程：查找最早碰撞 ---
            earliest_t, collided_widget, nx, ny = find_earliest_collision(widget, move_dx, move_dy)

            if earliest_t is None:
                widget.place(x=proposed_x, y=proposed_y)
                
            else:
                mx, my, mw, mh = get_widget_bounds(widget)
                sx, sy, sw, sh = get_widget_bounds(collided_widget)

                # 计算碰撞点
                collide_x = mx + move_dx * earliest_t
                collide_y = my + move_dy * earliest_t

                # 主方向：无缝隙贴边
                if nx == -1:     # A 左 -> B 右
                    new_x = sx - mw
                elif nx == 1:    # A 右 -> B 左
                    new_x = sx + sw
                else:
                    new_x = collide_x

                if ny == -1:     # A 上 -> B 下
                    new_y = sy - mh
                elif ny == 1:    # A 下 -> B 上
                    new_y = sy + sh
                else:
                    new_y = collide_y

                # 先放到贴边位置（不会有空隙）
                widget.place(x=int(new_x), y=int(new_y))

                # --------继续处理“滑动”------------
                # 剩余位移 = 沿未碰撞轴继续移动
                remaining_dx = move_dx * (1 - earliest_t)
                remaining_dy = move_dy * (1 - earliest_t)

                # 如果碰撞发生在 X 轴（nx != 0），允许沿 Y 轴滑动
                if nx != 0 and remaining_dy != 0:
                    try_y = int(new_y + remaining_dy)
                    if not is_overlapping_any_other_widget(widget, new_x, try_y):
                        widget.place(x=int(new_x), y=try_y)

                # 如果碰撞发生在 Y 轴（ny != 0），允许沿 X 轴滑动
                if ny != 0 and remaining_dx != 0:
                    try_x = int(new_x + remaining_dx)
                    if not is_overlapping_any_other_widget(widget, try_x, new_y):
                        widget.place(x=try_x, y=int(new_y))

            Label_Downtabel['text']=f'      ( {widget.winfo_x()} , {widget.winfo_y()} )      ( {widget.winfo_x()+widget.winfo_x()+widget.winfo_width()-1} , {widget.winfo_y()+widget.winfo_height()-1} )      [ {widget.winfo_width()} , {widget.winfo_height()} ]'  

        def draggable(tkwidget):
            #使控件可拖动，并将其添加到全局可拖动列表中
            
            # 绑定拖动事件
            tkwidget.bind("<Button-1>", mousedown, add='+')
            tkwidget.bind("<B1-Motion>", drag, add='+')
            DRAGGABLE_WIDGETS.append(tkwidget)         


        def close_Window_PlaceTextures(event=None):
            Window_MimodelUVMmerge.attributes('-disabled', 'false')
            Window_PlaceTextures.destroy()
            Window_MimodelUVMmerge.focus()

        def cancel_Window_PlaceTextures(event=None):
            nonlocal err
            err=False
            close_Window_PlaceTextures()
        Window_PlaceTextures = tk.Toplevel(Window_MimodelUVMmerge)
        Window_MimodelUVMmerge.attributes('-disabled', 'true')
        Window_PlaceTextures.title("贴图排布")
       ## Window_PlaceTextures.geometry("600x400") # 稍微增大窗口以便观察
        Window_PlaceTextures['bd']=0
        width=1400
        height=800
        screenwidth = Window_PlaceTextures.winfo_screenwidth()
        screenheight = Window_PlaceTextures.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        Window_PlaceTextures.geometry(geometry)
        Window_PlaceTextures.bind('<Escape>',cancel_Window_PlaceTextures)
        Window_PlaceTextures.focus()
        Window_PlaceTextures.protocol("WM_DELETE_WINDOW", cancel_Window_PlaceTextures)

        Frame_Window_PlaceTextures_cavan = tk.Frame(Window_PlaceTextures, bd=0,bg='SystemScrollBar')
        Frame_Window_PlaceTextures_cavan.pack(fill='both', expand=True)

        
        tk.Label(Window_PlaceTextures,text='按下回车键确定',bg='yellow',bd=0,anchor='w',height=2).pack(side='bottom',fill='x',)

        Label_Downtabel=tk.Label(Window_PlaceTextures,text='',bd=0,anchor='w',height=2)
        Label_Downtabel.pack(side='bottom',fill='x',)

        temp_ofx_all=0
        for p in all_texture_dict:
            temp_Photo=tk.PhotoImage(file=all_texture_dict[p],)
            temp_Button=tk.Label(Frame_Window_PlaceTextures_cavan, text=p, relief="solid", bd=1, anchor='center', compound='center', image=temp_Photo)
            temp_Button.place(x=temp_ofx_all,y=0,width=temp_Photo.width(),height=temp_Photo.height())
            temp_ofx_all+=temp_Photo.width()
            draggable(temp_Button)
            temp_Button.image=temp_Photo  # 保持引用，防止被垃圾回收

        def return_ok_place_textures(event=None):
            all_texture_offset_dict
            for widget in Frame_Window_PlaceTextures_cavan.winfo_children():
                if isinstance(widget, tk.Label):
                    x = widget.winfo_x()
                    y = widget.winfo_y()
                    texture_name = widget['text']
                    all_texture_offset_dict[texture_name] = [x, y]
            close_Window_PlaceTextures()
            

        Window_PlaceTextures.bind('<Return>',return_ok_place_textures)
        Window_PlaceTextures.iconbitmap(f"{resource_path}icon.ico")
        Window_PlaceTextures.wait_window(Window_PlaceTextures)

        return err

    def run_MimodelUVMmerge(event=None):
        global all_texture_dict,all_texture_offset_dict,new_texture_img
        all_texture_dict={}
        all_texture_offset_dict={}

        original_mimodel_file=Entry_original_mimodel_file.get().strip().replace('\\','/')

        new_mimodel_file=Entry_new_mimodel_file.get().strip().replace('\\','/')
        new_texture_file=Entry_new_texture_file.get().strip().replace('\\','/')
        
        if original_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='未选择原mimodel文件.',icon='error');Entry_original_mimodel_file.focus_set();return
        
        if new_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='未选择新mimodel文件.',icon='error');Entry_new_mimodel_file.focus_set();return
        if new_texture_file.replace(' ','')=='': MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='未选择新贴图文件.',icon='error');Entry_new_texture_file.focus_set();return
        if not os.path.exists(original_mimodel_file): MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='原mimodel文件不存在.',icon='error');Entry_original_mimodel_file.focus_set();return
        
        if os.path.exists(new_mimodel_file): MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='新mimodel型文件已存在.',icon='error');Entry_new_mimodel_file.focus_set();return
        if os.path.exists(new_texture_file): MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='新贴图文件已存在.',icon='error');Entry_new_texture_file.focus_set();return
        try:
            for child in Window_MimodelUVMmerge.winfo_children():
                if child.winfo_class()=='TButton':
                    child.config(state='disabled')
                elif child.winfo_class()=='TSpinbox' or child.winfo_class()=='TEntry':
                    child.config(state='readonly')
            loading_label=LoadingLabel(Window_MimodelUVMmerge,)
            loading_label.pack(fill='both',expand=True)
            Window_MimodelUVMmerge.update()

            with open(original_mimodel_file,'r',encoding='utf-8') as f:
                data_mimodel=json.loads(f.read())

            traverse_parts_shapes_set_temp_texture_key(data_mimodel) #为每个part设置好临时材质键值,同时扫描所有需要的贴图


            for key in all_texture_dict.keys():
                temp_file=InputBox(title=f'链接贴图 {key} 的文件',text='文件:',parent=Window_MimodelUVMmerge,default=f'{os.path.dirname(original_mimodel_file)}/{key}',canspace=True,canempty=False)
                
                if temp_file==None or temp_file.replace(' ','')=='':
                    #MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='必须链接材质文件.',icon='error')
                    for child in Window_MimodelUVMmerge.winfo_children():
                            if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                                child.config(state='normal')
                    loading_label.destroy()
                    Window_MimodelUVMmerge.update()
                    return
                temp_file=temp_file.replace('\\','/')

                if not os.path.exists(temp_file):
                    MessageBox(parent=Window_MimodelUVMmerge,title='错误',text='链接的材质文件不存在.',icon='error')
                    for child in Window_MimodelUVMmerge.winfo_children():
                        if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                                child.config(state='normal')
                    loading_label.destroy()
                    Window_MimodelUVMmerge.update()
                    
                    return

                all_texture_dict[key]=temp_file


            #---------这里需要修改------------
            """new_texture_size=[0,0]
            for key in all_texture_dict:
                temp_img=Image.open(all_texture_dict[key]).convert('RGBA')
                new_texture_size[0]+=temp_img.width
                new_texture_size[1]=max(new_texture_size[1],temp_img.height)
            
            new_texture_img=Image.new('RGBA', (new_texture_size[0] ,new_texture_size[1]), (0, 0, 0, 0))
            general_offset_x=0
            general_offset_y=0
            for key in all_texture_dict:#字典有序
                temp_img=Image.open(all_texture_dict[key]).convert('RGBA')
                new_texture_img.paste(temp_img,(general_offset_x,general_offset_y))
                all_texture_offset_dict[key]=[general_offset_x,general_offset_x+temp_img.width-1]
                general_offset_x+=temp_img.width
                print(all_texture_offset_dict)
                print('\n')"""
            
            result=run_DragDropTextrue()
            if result==False:
                for child in Window_MimodelUVMmerge.winfo_children():
                        if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                            child.config(state='normal')
                Window_MimodelUVMmerge.update()
                return
            new_texture_size=[0,0]
            # 计算新贴图的总尺寸
            for key in all_texture_dict:
                temp_img=Image.open(all_texture_dict[key]).convert('RGBA')
                offset = all_texture_offset_dict[key]  # 获取贴图偏移信息
                new_texture_size[0] = max(new_texture_size[0], offset[0] + temp_img.width)  # x + width
                new_texture_size[1] = max(new_texture_size[1], offset[1] + temp_img.height)  # y + height

            new_texture_img=Image.new('RGBA', (new_texture_size[0], new_texture_size[1]), (0, 0, 0, 0))

        
            # 放置贴图并记录偏移
            for key in all_texture_dict:
                temp_img=Image.open(all_texture_dict[key]).convert('RGBA')
                offset = all_texture_offset_dict[key]
                new_texture_img.paste(temp_img, (offset[0], offset[1]))
                #all_texture_offset_dict[key] = [offset[0], offset[1]]  # 记录x和y偏移


            for part in data_mimodel.get('parts', []):
                traverse_shapes_set_uv_offset(part)
            for part in data_mimodel.get('parts', []):
                traverse_parts_delete_texture_key(part)
        
            with open(new_mimodel_file,'w',encoding='utf-8') as f:
                f.write(json.dumps(data_mimodel, indent=4,ensure_ascii=False))

            new_texture_img.save(new_texture_file)


            MessageBox(parent=Window_MimodelUVMmerge,title='信息',text='处理完成.',icon='info')
        except Exception as e:
            MessageBox(parent=Window_MimodelUVMmerge,title='错误',text=f'处理文件时发生错误.\n详细信息: {e}',icon='error')
            return
        finally:
            for child in Window_MimodelUVMmerge.winfo_children():
                if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                    child.config(state='normal')
            loading_label.destroy()
            Window_MimodelUVMmerge.update()

        
    def close_Window_MimodelUVMmerge(event=None):
        Window_MimodelUVMmerge.destroy()
    Window_MimodelUVMmerge=tk.Toplevel(root)
    Window_MimodelUVMmerge.title('mimodel贴图合并工具')
    width=510
    height=220
    screenwidth = Window_MimodelUVMmerge.winfo_screenwidth()
    screenheight = Window_MimodelUVMmerge.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Window_MimodelUVMmerge.geometry(geometry)
    Window_MimodelUVMmerge.resizable(0,0)
    Window_MimodelUVMmerge.bind('<Escape>',close_Window_MimodelUVMmerge)
    Window_MimodelUVMmerge.focus()

    tk.Label(Window_MimodelUVMmerge,text='原mimodel文件路径: ',anchor='w').place(x=20,y=20,width=170,height=30)
    Entry_original_mimodel_file=ttk.Entry(Window_MimodelUVMmerge,)
    Entry_original_mimodel_file.place(x=200,y=20,width=230,height=30)
    def browse_original_mimodel_file():
        file_path = filedialog.askopenfilename(parent=Window_MimodelUVMmerge,filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_original_mimodel_file.delete(0, 'end')
            Entry_original_mimodel_file.insert(0, file_path)
    Button_browse_original_mimodel_file=ttk.Button(Window_MimodelUVMmerge,text='...',command=browse_original_mimodel_file)
    Button_browse_original_mimodel_file.place(x=450,y=20,width=40,height=30)


    tk.Label(Window_MimodelUVMmerge,text='新mimodel文件路径: ',anchor='w').place(x=20,y=70,width=170,height=30)
    Entry_new_mimodel_file=ttk.Entry(Window_MimodelUVMmerge,)
    Entry_new_mimodel_file.place(x=200,y=70,width=230,height=30)
    def browse_new_mimodel_file():
        file_path = filedialog.asksaveasfilename(parent=Window_MimodelUVMmerge,defaultextension='.mimodel',filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_mimodel_file.delete(0, 'end')
            Entry_new_mimodel_file.insert(0, file_path)
    Button_browse_new_mimodel_file=ttk.Button(Window_MimodelUVMmerge,text='...',command=browse_new_mimodel_file)
    Button_browse_new_mimodel_file.place(x=450,y=70,width=40,height=30)



    tk.Label(Window_MimodelUVMmerge,text='新贴图文件路径: ',anchor='w').place(x=20,y=120,width=170,height=30)
    Entry_new_texture_file=ttk.Entry(Window_MimodelUVMmerge,)
    Entry_new_texture_file.place(x=200,y=120,width=230,height=30)
    def browse_new_texture_file():
        file_path = filedialog.asksaveasfilename(parent=Window_MimodelUVMmerge,defaultextension='.png',filetypes=[("png文件", "*.png"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_texture_file.delete(0, 'end')
            Entry_new_texture_file.insert(0, file_path)
    Button_browse_new_texture_file=ttk.Button(Window_MimodelUVMmerge,text='...',command=browse_new_texture_file)
    Button_browse_new_texture_file.place(x=450,y=120,width=40,height=30)



    Window_MimodelUVMmerge.bind('<Return>',run_MimodelUVMmerge)
    Button_start=ttk.Button(Window_MimodelUVMmerge,text='确定',default='active',command=run_MimodelUVMmerge)
    Button_start.place(x=410,y=170,width=80,height=30)

    #ttk.Button(Window_MimodelUVMmerge,text='取消',command=close_Window_MimodelUVMmerge).place(x=410,y=170,width=80,height=30)

    Window_MimodelUVMmerge.iconbitmap(f'{resource_path}icon.ico')
    Window_MimodelUVMmerge.wait_window(Window_MimodelUVMmerge)

def MimodelUVSeparationAndFinishing():
    def hex_alpha_to_rgba(hex_color_str, alpha_float,):
        """
        将 (带#的十六进制颜色字符串, 0到1的透明度百分比) 元组
        转换为 RGBA (R, G, B, A) 整数元组 (0-255)。

        :param hex_color_str: 形式如 "#RRGGBB" 或 "#RGB" 的十六进制颜色字符串。
        :param alpha_float: 0.0 (完全透明) 到 1.0 (完全不透明) 的浮点数。
        :return: 包含 (R, G, B, A) 整数值 (0-255) 的元组。
        """
        # 1. 转换十六进制颜色到 RGB 整数元组
        # ImageColor.getrgb() 可以处理 #RGB 和 #RRGGBB 格式
        try:
            rgb_tuple = ImageColor.getrgb(hex_color_str)
            
            # 对于标准的十六进制颜色，getrgb() 返回 (R, G, B) 三个值
            r, g, b = rgb_tuple
        except ValueError as e:
            # 如果颜色字符串不正确，会抛出 ValueError
            raise ValueError(f"无效的十六进制颜色字符串 '{hex_color_str}': {e}")

        # 2. 转换 0.0-1.0 的浮点数 Alpha 值到 0-255 的整数 A 值
        


        # 确保浮点数在有效范围内 [0.0, 1.0]
        # 使用 max/min 来“钳制” (clamp) 数值，防止输入如 -0.1 或 1.5 导致错误。
        clamped_alpha = max(0.0, min(1.0, alpha_float))
        
        # 将浮点数 (0.0 - 1.0) 乘以 255 并四舍五入到最近的整数
        # A=0.0 -> 0; A=1.0 -> 255; A=0.5 -> 128
        a_int = round(clamped_alpha * 255)
        
        # 3. 组合并返回 RGBA 元组
        return (r, g, b, a_int)

    def mix_colors(original_color, mix_color, mix_percent,allow_alpha_reset=True ):
        """
        将两个颜色混合在一起，并返回混合后的颜色。

        :param original_color: 原始颜色，格式为 (R, G, B, A)。
        :param mix_color: 要混合的颜色，格式为 (R, G, B, A)。
        :param mix_percent: 混合百分比，范围从 0.0 到 1.0。
        :return: 混合后的颜色，格式为 (R, G, B, A)。
        """
        r = round(original_color[0] * (1 - mix_percent) + mix_color[0] * mix_percent)
        g = round(original_color[1] * (1 - mix_percent) + mix_color[1] * mix_percent)
        b = round(original_color[2] * (1 - mix_percent) + mix_color[2] * mix_percent)
        if allow_alpha_reset==True:
            a = round(original_color[3] * (1 - mix_percent) + mix_color[3] * mix_percent)
        else:
            a=original_color[3]
        return ( r, g, b,a)

    def process_shapes(shapes):
        global img_old,img_new,offset_x,offset_y,row_max_height,new_mimodel_file,new_texture_file
        
        for i, shape in enumerate(shapes):
            # 在这里对 shape 进行处理
            if shape['type']=='plane':
                plane_size=(math.ceil(abs(shape['to'][0]-shape['from'][0])), 
                            math.ceil(abs(shape['to'][1]-shape['from'][1])),
                            0)
                plane_x1=shape['uv'][0]
                plane_y1=shape['uv'][1]
                plane_x2=plane_x1+plane_size[0]
                plane_y2=plane_y1+plane_size[1]



                crop_temp=img_old.crop((plane_x1,plane_y1,plane_x2,plane_y2))
                if offset_x+crop_temp.size[0]>img_new.size[0]  and offset_x != 0:
                    offset_x = 0 
                    offset_y += row_max_height 
                    row_max_height = 0 
                
                draw_crop_temp = ImageDraw.Draw(crop_temp)
                if Var_not_reset_color_settings.get()==False:
                    for width_x in range(crop_temp.size[0]):
                        for height_y in range(crop_temp.size[1]):
                            colorpoint_original=crop_temp.getpixel((width_x,height_y))
                            if 'color_mix' not in shape:
                                shape['color_mix']='#000000'
                            if 'color_mix_percent' not in shape:
                                shape['color_mix_percent']=0
                            if 'color_alpha' not in shape :
                                shape['color_alpha']=1
                            colorpoint_mixed_color=mix_colors(colorpoint_original,hex_alpha_to_rgba(shape['color_mix'],shape['color_alpha']),shape['color_mix_percent'],allow_alpha_reset=False if Var_not_reset_alpha_settings.get() else True)
                            draw_crop_temp.rectangle([width_x, height_y, width_x, height_y], fill=colorpoint_mixed_color)
                    del shape['color_mix']
                    del shape['color_mix_percent']
                    if Var_not_reset_alpha_settings.get()==False:
                        del shape['color_alpha']

                shape['uv']=[offset_x,offset_y]


            
            if shape['type']=='block':
                block_size=(math.ceil(abs(shape['to'][0]-shape['from'][0])),math.ceil(abs(shape['to'][1]-shape['from'][1])),math.ceil(abs(shape['to'][2]-shape['from'][2])))
                block_front_leftup_x = shape['uv'][0]
                block_front_leftup_y = shape['uv'][1]
                block_x1 = block_front_leftup_x - block_size[2]
                block_y1 = block_front_leftup_y - block_size[2]
                block_x2 = block_x1 + block_size[0] *2 + block_size[2]*2
                block_y2 = block_y1 + block_size[2] + block_size[1]

                crop_temp=img_old.crop((block_x1,block_y1,block_x2,block_y2))

                draw_crop_temp = ImageDraw.Draw(crop_temp)
                if Var_not_reset_color_settings.get()==False:
                    for width_x in range(crop_temp.size[0]):
                        for height_y in range(crop_temp.size[1]):
                            colorpoint_original=crop_temp.getpixel((width_x,height_y))
                            if 'color_mix' not in shape:
                                shape['color_mix']='#000000'
                            if 'color_mix_percent' not in shape:
                                shape['color_mix_percent']=0
                            if 'color_alpha' not in shape:
                                shape['color_alpha']=1
                            colorpoint_mixed_color=mix_colors(colorpoint_original,hex_alpha_to_rgba(shape['color_mix'],shape['color_alpha']),shape['color_mix_percent'],allow_alpha_reset=False if Var_not_reset_alpha_settings.get() else True)
                            draw_crop_temp.rectangle([width_x, height_y, width_x, height_y], fill=colorpoint_mixed_color)
                    del shape['color_mix']
                    del shape['color_mix_percent']
                    if Var_not_reset_alpha_settings.get()==False:
                        del shape['color_alpha']


                # 填充矩形区域
                # xy 是一个包含两个点的元组：[ (x0, y0), (x1, y1) ]
                # 或一个包含四个数值的元组：[ x0, y0, x1, y1 ]
                draw_crop_temp.rectangle([
                                            0,
                                            0,
                                            block_size[2]-1,
                                            block_size[2]-1,
                                        ],
                                        fill=(0,0,0,0))
                draw_crop_temp.rectangle([
                                            block_size[0]*2+block_size[2],
                                            0,
                                            block_size[0]*2+block_size[2]*2-1 ,
                                            block_size[2]-1
                                        ], 
                                        fill=(0,0,0,0))
                
                
                if offset_x+crop_temp.size[0]>img_new.size[0] :
                    offset_x = 0 
                    offset_y += row_max_height 
                    row_max_height = 0 
                if offset_y+crop_temp.size[1]>img_new.size[1] :
                    #报错不在这里
                    return False
            
                
                shape['uv']=[offset_x+block_size[2],offset_y+block_size[2]]

            img_new.paste(crop_temp,(offset_x,offset_y))
            img_new.save(new_texture_file)

            offset_x+=crop_temp.size[0]

            row_max_height = max(row_max_height, crop_temp.size[1]) 

        new_shape = shape  
        shapes[i] = new_shape  # 写回原数据

        return True

    def traverse_parts(part):
        # 如果有 shapes 列表，处理它
        if 'shapes' in part and isinstance(part['shapes'], list):
            r = process_shapes(part['shapes'])
            if r==False:
                return False
        # 如果有子 parts，递归处理
        if 'parts' in part and isinstance(part['parts'], list):
            for subpart in part['parts']:
                traverse_parts(subpart)

    def run_MimodelUVSeparationAndFinishing(event=None):

        global img_old,img_new,offset_x,offset_y,row_max_height,new_mimodel_file,new_texture_file,new_texture_width,new_texture_height
        original_mimodel_file=Entry_original_mimodel_file.get().strip().replace('\\','/')
        original_texture_file=Entry_original_texture_file.get().strip().replace('\\','/')
        new_mimodel_file=Entry_new_mimodel_file.get().strip().replace('\\','/')
        new_texture_file=Entry_new_texture_file.get().strip().replace('\\','/')
        
        if original_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='未选择原mimodel文件.',icon='error');Entry_original_mimodel_file.focus_set();return
        if original_texture_file.replace(' ','')=='': MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='未选择原贴图文件.',icon='error');Entry_original_texture_file.focus_set();return
        if new_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='未选择新mimodel文件.',icon='error');Entry_new_mimodel_file.focus_set();return
        if new_texture_file.replace(' ','')=='': MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='未选择新贴图文件.',icon='error');Entry_new_texture_file.focus_set();return
        if not os.path.exists(original_mimodel_file): MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='原mimodel文件不存在.',icon='error');Entry_original_mimodel_file.focus_set();return
        if not os.path.exists(original_texture_file): MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='原贴图文件不存在.',icon='error');Entry_original_texture_file.focus_set();return
        if os.path.exists(new_mimodel_file): MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='新mimodel型文件已存在.',icon='error');Entry_new_mimodel_file.focus_set();return
        if os.path.exists(new_texture_file): MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='新贴图文件已存在.',icon='error');Entry_new_texture_file.focus_set();return

        try: new_texture_width=int(Spinbox_new_texture_width.get())
        except: MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='新贴图宽输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return
        try: new_texture_height=int(Spinbox_new_texture_height.get())
        except: MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='新贴图高输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return

        try:
            for child in Window_MimodelUVSeparationAndFinishing.winfo_children():
                if child.winfo_class()=='TButton':
                    child.config(state='disabled')
                elif child.winfo_class() in ('TSpinbox','TEntry','TCheckbutton'):
                    child.config(state='readonly')
            loading_label=LoadingLabel(Window_MimodelUVSeparationAndFinishing,)
            loading_label.pack(fill='both',expand=True)
            Window_MimodelUVSeparationAndFinishing.update()


            with open(original_mimodel_file,'r',encoding='utf-8') as f:
                data_mimodel=json.loads(f.read())
            img_old=Image.open(original_texture_file).convert('RGBA')
            img_new=Image.new('RGBA', (new_texture_width ,new_texture_height), (0, 0, 0, 0))
            offset_x=0
            offset_y=0
            row_max_height = 0
            # 假设 data_mimodel 是你的模型数据
            # traverse_parts(data_mimodel)  # 如果顶层就是 parts
            for part in data_mimodel.get('parts', []):
                if traverse_parts(part) ==False:
                    MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text='新贴图尺寸不足,无法继续排布.',icon='error')
                    for child in Window_MimodelUVSeparationAndFinishing.winfo_children():
                        if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton','TCheckbutton'):
                            child.config(state='normal')
                    loading_label.destroy()
                    Window_MimodelUVSeparationAndFinishing.update()
                    return
            
            with open(new_mimodel_file,'w',encoding='utf-8') as f:
                f.write(json.dumps(data_mimodel, indent=4,ensure_ascii=False))
            MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='信息',text='处理完成.',icon='info')
        except Exception as e:
            MessageBox(parent=Window_MimodelUVSeparationAndFinishing,title='错误',text=f'处理文件时发生错误.\n详细信息: {e}',icon='error')
            return
        finally:
            for child in Window_MimodelUVSeparationAndFinishing.winfo_children():
                if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton','TCheckbutton'):
                    child.config(state='normal')
            loading_label.destroy()
            Window_MimodelUVSeparationAndFinishing.update()

    def exit_app(event=None):
        Window_MimodelUVSeparationAndFinishing.destroy()
    Window_MimodelUVSeparationAndFinishing=tk.Toplevel(root)
    Window_MimodelUVSeparationAndFinishing.title('mimodelUV分离与整理')
    width=510
    height=420
    screenwidth = Window_MimodelUVSeparationAndFinishing.winfo_screenwidth()
    screenheight = Window_MimodelUVSeparationAndFinishing.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Window_MimodelUVSeparationAndFinishing.geometry(geometry)
    Window_MimodelUVSeparationAndFinishing.resizable(0,0)
    Window_MimodelUVSeparationAndFinishing.bind('<Escape>',exit_app)
    Window_MimodelUVSeparationAndFinishing.focus()

    tk.Label(Window_MimodelUVSeparationAndFinishing,text='仅支持单贴图,多贴图需先使用UV合并工具转换.不支持"混合材质"项.',anchor='w',fg="#C90000").place(x=20,y=320,width=470,height=30)

    tk.Label(Window_MimodelUVSeparationAndFinishing,text='原mimodel文件路径: ',anchor='w').place(x=20,y=20,width=170,height=30)
    Entry_original_mimodel_file=ttk.Entry(Window_MimodelUVSeparationAndFinishing,)
    Entry_original_mimodel_file.place(x=200,y=20,width=230,height=30)
    def browse_original_mimodel_file():
        file_path = filedialog.askopenfilename(parent=Window_MimodelUVSeparationAndFinishing,filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_original_mimodel_file.delete(0, 'end')
            Entry_original_mimodel_file.insert(0, file_path)
    Button_browse_original_mimodel_file=ttk.Button(Window_MimodelUVSeparationAndFinishing,text='...',command=browse_original_mimodel_file)
    Button_browse_original_mimodel_file.place(x=450,y=20,width=40,height=30)


    tk.Label(Window_MimodelUVSeparationAndFinishing,text='原贴图文件路径: ',anchor='w').place(x=20,y=70,width=170,height=30)
    Entry_original_texture_file=ttk.Entry(Window_MimodelUVSeparationAndFinishing,)
    Entry_original_texture_file.place(x=200,y=70,width=230,height=30)
    def browse_original_texture_file():
        file_path = filedialog.askopenfilename(parent=Window_MimodelUVSeparationAndFinishing,filetypes=[("png文件", "*.png"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_original_texture_file.delete(0, 'end')
            Entry_original_texture_file.insert(0, file_path)
    Button_browse_original_texture_file=ttk.Button(Window_MimodelUVSeparationAndFinishing,text='...',command=browse_original_texture_file)
    Button_browse_original_texture_file.place(x=450,y=70,width=40,height=30)


    tk.Label(Window_MimodelUVSeparationAndFinishing,text='新mimodel文件路径: ',anchor='w').place(x=20,y=120,width=170,height=30)
    Entry_new_mimodel_file=ttk.Entry(Window_MimodelUVSeparationAndFinishing,)
    Entry_new_mimodel_file.place(x=200,y=120,width=230,height=30)
    def browse_new_mimodel_file():
        file_path = filedialog.asksaveasfilename(parent=Window_MimodelUVSeparationAndFinishing,defaultextension='.mimodel',filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_mimodel_file.delete(0, 'end')
            Entry_new_mimodel_file.insert(0, file_path)
    Button_browse_new_mimodel_file=ttk.Button(Window_MimodelUVSeparationAndFinishing,text='...',command=browse_new_mimodel_file)
    Button_browse_new_mimodel_file.place(x=450,y=120,width=40,height=30)


    tk.Label(Window_MimodelUVSeparationAndFinishing,text='新贴图文件路径: ',anchor='w').place(x=20,y=170,width=170,height=30)
    Entry_new_texture_file=ttk.Entry(Window_MimodelUVSeparationAndFinishing,)
    Entry_new_texture_file.place(x=200,y=170,width=230,height=30)
    def browse_new_texture_file():
        file_path = filedialog.asksaveasfilename(parent=Window_MimodelUVSeparationAndFinishing,defaultextension='.png',filetypes=[("png文件", "*.png"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_texture_file.delete(0, 'end')
            Entry_new_texture_file.insert(0, file_path)
    Button_browse_new_texture_file=ttk.Button(Window_MimodelUVSeparationAndFinishing,text='...',command=browse_new_texture_file)
    Button_browse_new_texture_file.place(x=450,y=170,width=40,height=30)


    tk.Label(Window_MimodelUVSeparationAndFinishing,text='新贴图宽:',anchor='w').place(x=20,y=220,width=120,height=30)
    Spinbox_new_texture_width=ttk.Spinbox(Window_MimodelUVSeparationAndFinishing,from_=16,to=float('inf'),increment=16)
    Spinbox_new_texture_width.place(x=200,y=220,width=230,height=30)
    Spinbox_new_texture_width.insert(0,256)

    tk.Label(Window_MimodelUVSeparationAndFinishing,text='新贴图高:',anchor='w').place(x=20,y=270,width=120,height=30)
    Spinbox_new_texture_height=ttk.Spinbox(Window_MimodelUVSeparationAndFinishing,from_=16,to=float('inf'),increment=16)
    Spinbox_new_texture_height.place(x=200,y=270,width=230,height=30)
    Spinbox_new_texture_height.insert(0,256)


    def update_checkbutton(event=None):
        if Var_not_reset_color_settings.get()==True:
            Var_not_reset_alpha_settings.set(True)
            Checkbutton_not_reset_alpha_settings.config(state='disabled')
        else:
            Checkbutton_not_reset_alpha_settings.config(state='normal')

    ttk.Style().configure('NOT.TCheckbutton',anchor='w')
    Var_not_reset_color_settings=tk.BooleanVar()
    Var_not_reset_color_settings.set(True)
    Checkbutton_not_reset_color_settings=ttk.Checkbutton(Window_MimodelUVSeparationAndFinishing,text='保留MB颜色属性',command=update_checkbutton,variable=Var_not_reset_color_settings,style='NOT.TCheckbutton',onvalue=True,offvalue=False)
    Checkbutton_not_reset_color_settings.place(x=20,y=370,width=150,height=30)


    Var_not_reset_alpha_settings=tk.BooleanVar()
    Var_not_reset_alpha_settings.set(True)
    Checkbutton_not_reset_alpha_settings=ttk.Checkbutton(Window_MimodelUVSeparationAndFinishing,text='保留MB透明度属性(推荐)',command=update_checkbutton,variable=Var_not_reset_alpha_settings,style='NOT.TCheckbutton',onvalue=True,offvalue=False)
    Checkbutton_not_reset_alpha_settings.place(x=190,y=370,width=200,height=30)

    update_checkbutton()

    Window_MimodelUVSeparationAndFinishing.bind('<Return>',run_MimodelUVSeparationAndFinishing)
    Button_start=ttk.Button(Window_MimodelUVSeparationAndFinishing,text='确定',default='active',command=run_MimodelUVSeparationAndFinishing)
    Button_start.place(x=410,y=370,width=80,height=30)


    Window_MimodelUVSeparationAndFinishing.iconbitmap(f'{resource_path}icon.ico')
    Window_MimodelUVSeparationAndFinishing.mainloop()

def MimodelRenameRedDuplicateComponents():
    parts_names_dict={}
    count_id=0
    list_keys=[]

    def run_MimodelRenameRedDuplicateComponents(event=None):
        original_mimodel_file=Entry_original_mired_mimodel_file.get().strip()
        new_mimodel_file=Entry_new_mired_mimodel_file.get().strip()

        if original_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelRenameRedDuplicateComponents,title='错误',text='未选择原mimodel文件.',icon='error');Entry_original_mired_mimodel_file.focus_set();return
        if new_mimodel_file.replace(' ','')=='': MessageBox(parent=Window_MimodelRenameRedDuplicateComponents,title='错误',text='未选择新mimodel文件.',icon='error');Entry_new_mired_mimodel_file.focus_set();return
        if not os.path.exists(original_mimodel_file): MessageBox(parent=Window_MimodelRenameRedDuplicateComponents,title='错误',text='原mimodel文件不存在.',icon='error');Entry_original_mired_mimodel_file.focus_set();return
        if os.path.exists(new_mimodel_file): MessageBox(parent=Window_MimodelRenameRedDuplicateComponents,title='错误',text='新mimodel型文件已存在.',icon='error');Entry_new_mired_mimodel_file.focus_set();return

        try:
            for child in Window_MimodelRenameRedDuplicateComponents.winfo_children():
                if child.winfo_class()=='TButton':
                    child.config(state='disabled')
                elif child.winfo_class() in ('TSpinbox','TEntry'):
                    child.config(state='readonly')
            loading_label=LoadingLabel(Window_MimodelRenameRedDuplicateComponents,)
            loading_label.pack(fill='both',expand=True)
            Window_MimodelRenameRedDuplicateComponents.update()

            with open(original_mimodel_file,'r',encoding='utf-8') as f:
                data_mimodel=json.loads(f.read())

            for part in data_mimodel.get('parts', []):
                traverse_parts_count_and_tag(part)

            with open(new_mimodel_file,'w',encoding='utf-8') as f_new:
                f_new.write(json.dumps(data_mimodel, indent=4,ensure_ascii=False))
            MessageBox(parent=Window_MimodelRenameRedDuplicateComponents,title='信息',text='处理完成.',icon='info')
        except Exception as e:
            MessageBox(parent=Window_MimodelRenameRedDuplicateComponents,title='错误',text=f'处理文件时发生错误.\n详细信息: {e}',icon='error')
            return
        finally:
            for child in Window_MimodelRenameRedDuplicateComponents.winfo_children():
                if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                    child.config(state='normal')
            loading_label.destroy()
            Window_MimodelRenameRedDuplicateComponents.update()

    def traverse_parts_count_and_tag(part):
        nonlocal count_id, parts_names_dict, list_keys
        # 如果有子 parts，递归处理
        if 'parts' in part and isinstance(part['parts'], list):
            
            parts=part['parts']
            for i, subpart in enumerate(parts):
                subpart['mb_name']=subpart['name']
                parts[i] = subpart
                traverse_parts_count_and_tag(subpart)

    def close_Window_MimodelRenameRedDuplicateComponents(event=None):
        Window_MimodelRenameRedDuplicateComponents.destroy()
    Window_MimodelRenameRedDuplicateComponents=tk.Toplevel()
    Window_MimodelRenameRedDuplicateComponents.title('mimodel重命名红色重名组件')
    width=510
    height=170
    screenwidth = Window_MimodelRenameRedDuplicateComponents.winfo_screenwidth()
    screenheight = Window_MimodelRenameRedDuplicateComponents.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Window_MimodelRenameRedDuplicateComponents.geometry(geometry)
    Window_MimodelRenameRedDuplicateComponents.resizable(0,0)
    Window_MimodelRenameRedDuplicateComponents.bind('<Escape>',close_Window_MimodelRenameRedDuplicateComponents)
    Window_MimodelRenameRedDuplicateComponents.focus()

    tk.Label(Window_MimodelRenameRedDuplicateComponents,text='原mimodel文件路径: ',anchor='w').place(x=20,y=20,width=170,height=30)
    Entry_original_mired_mimodel_file=ttk.Entry(Window_MimodelRenameRedDuplicateComponents,)
    Entry_original_mired_mimodel_file.place(x=200,y=20,width=230,height=30)
    def browse_original_mired_mimodel_file():
        file_path = filedialog.askopenfilename(parent=Window_MimodelRenameRedDuplicateComponents,filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_original_mired_mimodel_file.delete(0, 'end')
            Entry_original_mired_mimodel_file.insert(0, file_path)
    Button_browse_mired_original_mimodel_file=ttk.Button(Window_MimodelRenameRedDuplicateComponents,text='...',command=browse_original_mired_mimodel_file)
    Button_browse_mired_original_mimodel_file.place(x=450,y=20,width=40,height=30)

    tk.Label(Window_MimodelRenameRedDuplicateComponents,text='新mimodel文件路径: ',anchor='w').place(x=20,y=70,width=170,height=30)
    Entry_new_mired_mimodel_file=ttk.Entry(Window_MimodelRenameRedDuplicateComponents,)
    Entry_new_mired_mimodel_file.place(x=200,y=70,width=230,height=30)
    def browse_new_mired_mimodel_file():
        file_path = filedialog.asksaveasfilename(parent=Window_MimodelRenameRedDuplicateComponents,defaultextension='.mimodel',filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_mired_mimodel_file.delete(0, 'end')
            Entry_new_mired_mimodel_file.insert(0, file_path)
    Button_browse_new_mired_mimodel_file=ttk.Button(Window_MimodelRenameRedDuplicateComponents,text='...',command=browse_new_mired_mimodel_file)
    Button_browse_new_mired_mimodel_file.place(x=450,y=70,width=40,height=30)


    Window_MimodelRenameRedDuplicateComponents.bind('<Return>',run_MimodelRenameRedDuplicateComponents)
    Button_start=ttk.Button(Window_MimodelRenameRedDuplicateComponents,text='确定',default='active',command=run_MimodelRenameRedDuplicateComponents)
    Button_start.place(x=410,y=120,width=80,height=30)

    Window_MimodelRenameRedDuplicateComponents.iconbitmap(f'{resource_path}icon.ico')
    Window_MimodelRenameRedDuplicateComponents.wait_window()

def BBmodelFaceToBoxUV():
    def close_Window_BBmodelFaceToBoxUV(event=None):
        Window_BBmodelFaceToBoxUV.destroy()

    Window_BBmodelFaceToBoxUV=tk.Toplevel(root)
    Window_BBmodelFaceToBoxUV.title('bbmodelUV逐面转箱式')
    width=510
    height=420
    screenwidth = Window_BBmodelFaceToBoxUV.winfo_screenwidth()
    screenheight = Window_BBmodelFaceToBoxUV.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Window_BBmodelFaceToBoxUV.geometry(geometry)
    Window_BBmodelFaceToBoxUV.resizable(0,0)
    Window_BBmodelFaceToBoxUV.bind('<Escape>',close_Window_BBmodelFaceToBoxUV)
    Window_BBmodelFaceToBoxUV.focus()

    tk.Label(Window_BBmodelFaceToBoxUV,text='原bb模型文件路径: ',anchor='w').place(x=20,y=20,width=170,height=30)
    Entry_original_bbmodel_file=ttk.Entry(Window_BBmodelFaceToBoxUV,)
    Entry_original_bbmodel_file.place(x=200,y=20,width=230,height=30)
    def browse_original_bbmodel_file():
        file_path = filedialog.askopenfilename(parent=Window_BBmodelFaceToBoxUV,filetypes=[("bbmodel文件", "*.bbmodel"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_original_bbmodel_file.delete(0, 'end')
            Entry_original_bbmodel_file.insert(0, file_path)
    Button_browse_original_bbmodel_file=ttk.Button(Window_BBmodelFaceToBoxUV,text='...',command=browse_original_bbmodel_file)
    Button_browse_original_bbmodel_file.place(x=450,y=20,width=40,height=30)



    tk.Label(Window_BBmodelFaceToBoxUV,text='原贴图文件路径: ',anchor='w').place(x=20,y=70,width=170,height=30)
    Entry_original_texture_file=ttk.Entry(Window_BBmodelFaceToBoxUV,)
    Entry_original_texture_file.place(x=200,y=70,width=230,height=30)
    def browse_original_texture_file():
        file_path = filedialog.askopenfilename(parent=Window_BBmodelFaceToBoxUV,filetypes=[("PNG文件", "*.png"), ("所有文件", "*.*")])
        
        if file_path!='' and file_path!=None:
            Entry_original_texture_file.delete(0, 'end')
            Entry_original_texture_file.insert(0, file_path)
    Button_browse_original_texture_file=ttk.Button(Window_BBmodelFaceToBoxUV,text='...',command=browse_original_texture_file)
    Button_browse_original_texture_file.place(x=450,y=70,width=40,height=30)



    tk.Label(Window_BBmodelFaceToBoxUV,text='新bb模型文件路径: ',anchor='w').place(x=20,y=120,width=170,height=30)
    Entry_new_bbmodel_file=ttk.Entry(Window_BBmodelFaceToBoxUV,)
    Entry_new_bbmodel_file.place(x=200,y=120,width=230,height=30)
    def browse_new_bbmodel_file():
        file_path = filedialog.asksaveasfilename(parent=Window_BBmodelFaceToBoxUV,defaultextension='.bbmodel',filetypes=[("bbmodel文件", "*.bbmodel"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_bbmodel_file.delete(0, 'end')
            Entry_new_bbmodel_file.insert(0, file_path)
    Button_browse_new_bbmodel_file=ttk.Button(Window_BBmodelFaceToBoxUV,text='...',command=browse_new_bbmodel_file)
    Button_browse_new_bbmodel_file.place(x=450,y=120,width=40,height=30)


    tk.Label(Window_BBmodelFaceToBoxUV,text='新贴图文件路径: ',anchor='w').place(x=20,y=170,width=170,height=30)
    Entry_new_texture_file=ttk.Entry(Window_BBmodelFaceToBoxUV,)
    Entry_new_texture_file.place(x=200,y=170,width=230,height=30)
    def browse_new_texture_file():
        file_path = filedialog.asksaveasfilename(parent=Window_BBmodelFaceToBoxUV,defaultextension='.png',filetypes=[("png文件", "*.png"), ("所有文件", "*.*")])
        if file_path!='' and file_path!=None:
            Entry_new_texture_file.delete(0, 'end')
            Entry_new_texture_file.insert(0, file_path)
    Button_browse_new_texture_file=ttk.Button(Window_BBmodelFaceToBoxUV,text='...',command=browse_new_texture_file)
    Button_browse_new_texture_file.place(x=450,y=170,width=40,height=30)

    tk.Label(Window_BBmodelFaceToBoxUV,text='新贴图宽:',anchor='w').place(x=20,y=220,width=120,height=30)
    Spinbox_new_texture_width=ttk.Spinbox(Window_BBmodelFaceToBoxUV,from_=16,to=float('inf'),increment=16)
    Spinbox_new_texture_width.place(x=200,y=220,width=230,height=30)
    Spinbox_new_texture_width.insert(0,256)

    tk.Label(Window_BBmodelFaceToBoxUV,text='新贴图高:',anchor='w').place(x=20,y=270,width=120,height=30)
    Spinbox_new_texture_height=ttk.Spinbox(Window_BBmodelFaceToBoxUV,from_=16,to=float('inf'),increment=16)
    Spinbox_new_texture_height.place(x=200,y=270,width=230,height=30)
    Spinbox_new_texture_height.insert(0,256)

    tk.Label(Window_BBmodelFaceToBoxUV,text='必须使用通用模型进行转换;不支持网格对象;逐面贴图不能拉伸.',anchor='w',fg="#C90000").place(x=20,y=320,width=470,height=30)

    def run_BBmodelFaceToBoxUV(event=None):
        if Entry_original_bbmodel_file.get().replace(' ','')=='': MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='未选择原bb模型文件.',icon='error');Entry_original_bbmodel_file.focus_set();return
        if Entry_original_texture_file.get().replace(' ','')=='': MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='未选择原贴图文件.',icon='error');Entry_original_texture_file.focus_set();return
        if Entry_new_bbmodel_file.get().replace(' ','')=='': MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='未选择新bb模型文件.',icon='error');Entry_new_bbmodel_file.focus_set();return
        if Entry_new_texture_file.get().replace(' ','')=='': MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='未选择新贴图文件.',icon='error');Entry_new_texture_file.focus_set();return
        if not os.path.exists(Entry_original_bbmodel_file.get()): MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='原bb模型文件不存在.',icon='error');Entry_original_bbmodel_file.focus_set();return
        if not os.path.exists(Entry_original_texture_file.get()): MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='原贴图文件不存在.',icon='error');Entry_original_texture_file.focus_set();return
        if os.path.exists(Entry_new_bbmodel_file.get()): MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='新bb模型文件已存在.',icon='error');Entry_new_bbmodel_file.focus_set();return
        if os.path.exists(Entry_new_texture_file.get()): MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='新贴图文件已存在.',icon='error');Entry_new_texture_file.focus_set();return

        try: int(Spinbox_new_texture_width.get())
        except: MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='新贴图宽输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return
        try: int(Spinbox_new_texture_height.get())
        except: MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='新贴图高输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return
        try:
            for child in Window_BBmodelFaceToBoxUV.winfo_children():
                if child.winfo_class()=='TButton':
                    child.config(state='disabled')
                elif child.winfo_class() in ('TSpinbox','TEntry'):
                    child.config(state='readonly')
            loading_label=LoadingLabel(Window_BBmodelFaceToBoxUV,)
            loading_label.pack(fill='both',expand=True)
            Window_BBmodelFaceToBoxUV.update()


            try :  
                with open(Entry_original_bbmodel_file.get(),'r',encoding='utf-8') as f:
                    data_original_bbmodel = json.load(f)
            except Exception as e:
                raise Exception(f'原bb模型文件读取或解析失败.\n详细信息: {e}')

            
            if data_original_bbmodel['meta']['box_uv']==True:
                raise Exception('原bb模型文件不是逐面UV.')
                #MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='原bb模型文件不是逐面UV.',icon='error')
                #Entry_original_bbmodel_file.focus_set()
                #return

            def change_(list_old):
                if list_old[0]>list_old[2] :
                    list_old=[list_old[2],list_old[1],list_old[0],list_old[3]]


                if list_old[1]>list_old[3]:
                    list_old=[list_old[0],list_old[3],list_old[2],list_old[1]]
                return list_old

            #检查开始,只处理文本.
            #处理项目: elements►<>►faces►<>►uv中的UV拉伸,让其与

            for i in data_original_bbmodel['elements']:
                block_size=(i['to'][0]-i['from'][0],i['to'][1]-i['from'][1],i['to'][2]-i['from'][2])
                block_name=i['name']
                dont_show_again=False
                for face_name, face_data in i['faces'].items():
                    #face_name指的是朝向而非名字
                    face_size=(face_data['uv'][2]-face_data['uv'][0],face_data['uv'][3]-face_data['uv'][1])
                    if face_name=='north':
                        if face_size[0]!=block_size[0] or face_size[1]!=block_size[1]:
                            if dont_show_again==True:
                                pass
                            elif MessageBox(parent=Window_BBmodelFaceToBoxUV,title='警告',text=f'方块 {block_name} 的 north 面出现拉伸错误,会导致贴图错误.\n(后续不会再提示.)',buttonmode=2,defaultfocus=1,icon='warning',text_true='忽略',text_false='终止')==False:
                                return
                            else:
                                dont_show_again=True
                    elif face_name=='south':
                        if face_size[0]!=block_size[0] or face_size[1]!=block_size[1]:
                            if dont_show_again==True:
                                pass
                            elif  MessageBox(parent=Window_BBmodelFaceToBoxUV,title='警告',text=f'方块 {block_name} 的 south 面出现拉伸错误,会导致贴图错误.\n(后续不会再提示.)',buttonmode=2,defaultfocus=1,icon='warning',text_true='忽略',text_false='终止')==False:
                                return
                            else:
                                dont_show_again=True
                    elif face_name=='east':
                        if face_size[0]!=block_size[2] or face_size[1]!=block_size[1]:
                            if dont_show_again==True:
                                pass
                            elif  MessageBox(parent=Window_BBmodelFaceToBoxUV,title='警告',text=f'方块 {block_name} 的 east 面出现拉伸错误,会导致贴图错误.\n(后续不会再提示.)',buttonmode=2,defaultfocus=1,icon='warning',text_true='忽略',text_false='终止')==False:
                                return
                            else:
                                dont_show_again=True
                    elif face_name=='west':
                        if face_size[0]!=block_size[2] or face_size[1]!=block_size[1]:
                            if dont_show_again==True:
                                pass
                            elif MessageBox(parent=Window_BBmodelFaceToBoxUV,title='警告',text=f'方块 {block_name} 的 west 面出现拉伸错误,会导致贴图错误.\n(后续不会再提示.)',buttonmode=2,defaultfocus=1,icon='warning',text_true='忽略',text_false='终止')==False:
                                return
                            else:
                                dont_show_again=True
                    elif face_name=='up':
                        if abs(face_size[0])!=block_size[0] or abs(face_size[1])!=block_size[2]:
                            if dont_show_again==True:
                                pass
                            elif MessageBox(parent=Window_BBmodelFaceToBoxUV,title='警告',text=f'方块 {block_name} 的 up 面出现拉伸错误,会导致贴图错误.\n(后续不会再提示.)',buttonmode=2,defaultfocus=1,icon='warning',text_true='忽略',text_false='终止')==False:
                                return
                            else:
                                dont_show_again=True
                    elif face_name=='down':
                        if abs(face_size[0])!=block_size[0] or abs(face_size[1])!=block_size[2]:
                            if dont_show_again==True:
                                pass
                            elif MessageBox(parent=Window_BBmodelFaceToBoxUV,title='警告',text=f'方块 {block_name} 的 down 面出现拉伸错误,会导致贴图错误.\n(后续不会再提示.)',buttonmode=2,defaultfocus=1,icon='warning',text_true='忽略',text_false='终止')==False:
                                return
                            else:
                                dont_show_again=True

            #检查结束
            #数据转换开始
            pil_original_texture=Image.open(Entry_original_texture_file.get()).convert('RGBA')
            pil_new_texture = Image.new('RGBA', (int(Spinbox_new_texture_width.get()),int(Spinbox_new_texture_height.get())), (0, 0, 0, 0))

            # 初始化偏移量和当前行的最大高度
            offset_x, offset_y = 0, 0
            row_max_height = 0  # <--- 在这里添加这一行

            # 遍历所有元素
            for idx, element in enumerate(data_original_bbmodel['elements']):
                block_size = ( 
                    int(element['to'][0] - element['from'][0]), 
                    int(element['to'][1] - element['from'][1]), 
                    int(element['to'][2] - element['from'][2]), 
                ) 

                # 计算该方块在UV图上展开后的总宽度和高度
                face_width = block_size[0] 
                face_height = block_size[1] 
                face_depth = block_size[2] 
                box_uv_width = face_depth * 2 + face_width * 2 
                box_uv_height = face_height + face_depth 

                # **核心修正：在绘制前检查是否需要换行**
                # 如果当前行放不下这个新方块，则先换行
                if offset_x + box_uv_width > pil_new_texture.size[0] and offset_x != 0: 
                    offset_x = 0 
                    offset_y += row_max_height 
                    row_max_height = 0 
                
                # 计算每个面的相对位置
                face_relative_pos_dict = {
                    'north': (face_depth, face_depth, face_width, face_height),
                    'south': (face_depth * 2 + face_width, face_depth, face_width, face_height),
                    'west': (0, face_depth, face_depth, face_height),
                    'east': (face_depth + face_width, face_depth, face_depth, face_height),
                    'up': (face_depth, 0, face_width, face_depth),
                    'down': (face_depth + face_width, 0, face_width, face_depth)
                }

                # 遍历处理每个面，进行绘制和UV坐标更新
                for side in ['north', 'south', 'west', 'east', 'up', 'down']:
                    original_uv = change_(element['faces'][side]['uv'])
                    temp_picture = pil_original_texture.crop((
                        original_uv[0], original_uv[1],
                        original_uv[2], original_uv[3],
                    ))
                    
                    # 计算在新贴图上的绝对位置 (使用修正后的offset_x, offset_y)
                    new_x = face_relative_pos_dict[side][0] + offset_x 
                    new_y = face_relative_pos_dict[side][1] + offset_y 
                    
                    pil_new_texture.paste(temp_picture, (new_x, new_y))
                    
                    # 更新模型JSON中的UV坐标
                    data_original_bbmodel['elements'][idx]['faces'][side]['uv'] = [
                        new_x, new_y,
                        new_x + face_relative_pos_dict[side][2],
                        new_y + face_relative_pos_dict[side][3]
                    ]
                
                # 设置方块的UV模式和UV偏移
                data_original_bbmodel['elements'][idx]['box_uv'] = True
                data_original_bbmodel['elements'][idx]['uv_offset'] = [offset_x, offset_y]
            
                # 更新下一个方块的起始X坐标
                offset_x += box_uv_width 
                # 更新当前行的最大高度，为下一次可能的换行做准备
                row_max_height = max(row_max_height, box_uv_height) 


            data_original_bbmodel['meta']['box_uv']=True

            try:
                with open(Entry_new_bbmodel_file.get(),'w',encoding='utf-8') as f:
                    json.dump(data_original_bbmodel,f,indent=1,ensure_ascii=False)
            except Exception as e:
                raise Exception(f'新bb模型文件写入失败.\n详细信息: {e}')
                #MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text=,icon='error')
                #Entry_new_bbmodel_file.focus_set()
                #return
            try:
                pil_new_texture.save(Entry_new_texture_file.get())
            except Exception as e:
                raise Exception(f'新贴图文件写入失败.\n详细信息: {e}')
                #MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text='新贴图文件写入失败.\n详细信息: '+str(e),icon='error')
                #Entry_new_texture_file.focus_set()
                #return
            MessageBox(parent=Window_BBmodelFaceToBoxUV,title='信息',text='模型UV模式转换完成.',icon='info')
        except Exception as e:
            MessageBox(parent=Window_BBmodelFaceToBoxUV,title='错误',text=f'处理时发生错误.\n详细信息: {e}',icon='error')
            return
        finally:
            for child in Window_BBmodelFaceToBoxUV.winfo_children():
                if child.winfo_class() in ('TButton','TSpinbox','TEntry'):
                    child.config(state='normal')
            loading_label.destroy()
            Window_BBmodelFaceToBoxUV.update()
    Window_BBmodelFaceToBoxUV.bind('<Return>',run_BBmodelFaceToBoxUV)
    Button_start=ttk.Button(Window_BBmodelFaceToBoxUV,text='确定',default='active',command=run_BBmodelFaceToBoxUV)
    Button_start.place(x=410,y=370,width=80,height=30)

    Window_BBmodelFaceToBoxUV.iconbitmap(f"{resource_path}icon.ico")
    Window_BBmodelFaceToBoxUV.wait_window(Window_BBmodelFaceToBoxUV)

def HexcolorToPixelImage():
    def close_Window_HexcolorToPixelImage(event=None):
        Window_HexcolorToPixelImage.destroy()
        #sys.exit()
    Window_HexcolorToPixelImage=tk.Toplevel(root)
    Window_HexcolorToPixelImage.title('多行颜色数值转像素图像&渐变色运算器')
    width=700
    height=500
    screenwidth = Window_HexcolorToPixelImage.winfo_screenwidth()
    screenheight = Window_HexcolorToPixelImage.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Window_HexcolorToPixelImage.geometry(geometry)
    Window_HexcolorToPixelImage.resizable(0,0)
    Window_HexcolorToPixelImage.bind('<Escape>',close_Window_HexcolorToPixelImage)
    Window_HexcolorToPixelImage.focus()

    def generate_gradient(start_hex, end_hex, n):
        # 去掉 # 号并转换为 RGB 元组
        def hex_to_rgb(hex_str):
            hex_str = hex_str.lstrip('#')
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

        # 将 RGB 转换为十六进制字符串
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*rgb)

        start_rgb = hex_to_rgb(start_hex)
        end_rgb = hex_to_rgb(end_hex)
        
        # 总段数为 n + 1 (例如插入1个数，就分2段)
        steps = n + 1
        gradient_list = []

        for i in range(steps + 1):
            # 计算当前步数的 RGB 分量
            curr_rgb = tuple(
                int(start_rgb[j] + (end_rgb[j] - start_rgb[j]) * i / steps)
                for j in range(3)
            )
            gradient_list.append(rgb_to_hex(curr_rgb).upper())

        return gradient_list

    def high_contrast_color(hex_color):
        # 1. 解析 RGB 颜色
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # 2. 计算人眼感知的亮度 (Luminance)
        # 权重系数：绿色最亮，红色次之，蓝色最暗
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        
        # 3. 根据亮度返回黑或白
        # 255 的一半是 127.5
        return "#000000" if brightness > 127.5 else "#FFFFFF"

    def update_Text_preview_colors(*args):
        Text_preview_colors['state']='normal'
        Text_preview_colors.delete('0.0','end')
        Text_preview_colors['state']='disabled'

        try:
            step_count=int(Var_step_count.get())
            if step_count<1:
                return
            begin_color='#'+Var_begin_color.get().strip().replace('#','')
            end_color='#'+Var_end_color.get().strip().replace('#','')
            tk.Label(Window_HexcolorToPixelImage,bg=begin_color)
            tk.Label(Window_HexcolorToPixelImage,bg=end_color)
            gradient_list=generate_gradient(begin_color,end_color,step_count)
        except:
            return
        
        Text_preview_colors['state']='normal'
        for i in gradient_list:
            Label_preview_step_color=tk.Label(Text_preview_colors,width=10,height=1,bg=i,fg=high_contrast_color(i),text=i)
            Text_preview_colors.window_create('end',window=Label_preview_step_color)
            Text_preview_colors.insert('end','\n')
        Text_preview_colors['state']='disabled'
        

    tk.Label(Window_HexcolorToPixelImage,text='渐变色运算器:',anchor='w',).place(x=20,y=20,width=140,height=30)

    Var_begin_color=tk.StringVar()
    Var_begin_color.set('')

    Var_begin_color.trace_add("write", update_Text_preview_colors)
    tk.Label(Window_HexcolorToPixelImage,text='起始颜色:',anchor='w',).place(x=20,y=70,width=100,height=30)
    Entry_begin_color=ttk.Entry(Window_HexcolorToPixelImage,textvariable=Var_begin_color)
    Entry_begin_color.place(x=120,y=70,width=100,height=30)

    Var_end_color=tk.StringVar()
    Var_end_color.set('')
    Var_end_color.trace_add("write", update_Text_preview_colors)
    tk.Label(Window_HexcolorToPixelImage,text='结束颜色:',anchor='w',).place(x=20,y=120,width=140,height=30)
    Entry_end_color=ttk.Entry(Window_HexcolorToPixelImage,textvariable=Var_end_color)
    Entry_end_color.place(x=120,y=120,width=100,height=30)

    Var_step_count=tk.StringVar()
    Var_step_count.set('5')
    Var_step_count.trace_add("write", update_Text_preview_colors)
    tk.Label(Window_HexcolorToPixelImage,text='步进数量:',anchor='w',).place(x=20,y=170,width=100,height=30)
    Spinbox_step_count=ttk.Spinbox(Window_HexcolorToPixelImage,from_=1,to=float('inf'),textvariable=Var_step_count)
    Spinbox_step_count.place(x=120,y=170,width=100,height=30)

    def copy_gradient_colors():
        color_text=""
        for widget in Text_preview_colors.winfo_children():
            if widget.winfo_class()=='Label':
                widget_value=widget['text']
                if widget_value!='':
                    color_text+=widget_value+'\n'
        pyperclip.copy(color_text.strip())
    Button_copy_gradient_colors=ttk.Button(Window_HexcolorToPixelImage,text='复制',command=copy_gradient_colors)
    Button_copy_gradient_colors.place(x=20,y=220,width=200,height=50)

    def on_tab(event):
        event.widget.tk_focusNext().focus()
        return "break"
    
    Text_preview_colors=tk.Text(Window_HexcolorToPixelImage,bd=1,relief='solid',font='TkDefaultFont',wrap='none',state='disabled')
    Text_preview_colors.place(x=240,y=50,width=140,height=380)
    Text_preview_colors.bind('<Tab>',on_tab)
    
    Scroll_Text_preview_colors_y=ttk.Scrollbar(Window_HexcolorToPixelImage,orient='vertical',command=Text_preview_colors.yview)
    Scroll_Text_preview_colors_y.place(x=380,y=50,width=20,height=380)
    Text_preview_colors.config(yscrollcommand=Scroll_Text_preview_colors_y.set)
    #按钮y=230

    def fill_in_Text_colors():
        Text_colors.delete('0.0','end')
        for widget in Text_preview_colors.winfo_children():
            if widget.winfo_class()=='Label':
                widget_value=widget['text']
                if widget_value!='':
                    Text_colors.insert('end',widget_value+'\n')
        Text_colors.focus()

    Button_apply_preview_colors=ttk.Button(Window_HexcolorToPixelImage,text='填入→',command=fill_in_Text_colors)
    Button_apply_preview_colors.place(x=420,y=230,width=80,height=30)



    tk.Label(Window_HexcolorToPixelImage,text='多行颜色Hex值:',anchor='w').place(x=520,y=20,width=140,height=20)


    Text_colors=tk.Text(Window_HexcolorToPixelImage,bd=1,relief='solid',font='TkDefaultFont',wrap='none')
    Text_colors.place(x=520,y=50,width=140,height=380)
    Text_colors.focus()
    Text_colors.bind('<Tab>',on_tab)


    Scroll_Text_colors_y=ttk.Scrollbar(Window_HexcolorToPixelImage,orient='vertical',command=Text_colors.yview)
    Scroll_Text_colors_y.place(x=660,y=50,width=20,height=380)

    Text_colors.config(yscrollcommand=Scroll_Text_colors_y.set)

    def draw_colors(event=None):
        temp_colors_list=Text_colors.get('0.0','end-1c').replace(' ','').replace('\t','').replace('#','')
        temp_colors_list=temp_colors_list.split('\n')
        colors_list=[]
        for i in range(len(temp_colors_list)):
            if temp_colors_list[i]!='':
                colors_list.append(temp_colors_list[i])
        
        if len(colors_list)==0:
            win32api.MessageBeep()
            Text_colors.focus()
            return
        for i in range(len(colors_list)):
            colors_list[i]=f'#{colors_list[i]}'

        file_path = filedialog.asksaveasfilename(parent=Window_HexcolorToPixelImage,initialfile='多行颜色数值转像素图像.png',defaultextension='.png',filetypes=[("png文件", "*.png")])
        if file_path!='' and file_path!=None:
            try:
                pic=Image.new('RGB',(1,len(colors_list)),)
                drawable_pic=ImageDraw.Draw(pic)

                for i in range(len(colors_list)):
                    drawable_pic.point((0, i), fill=str(colors_list[i]))

                pic.save(file_path)
            except Exception as e:
                MessageBox(parent=Window_HexcolorToPixelImage,title='错误',text=f'绘制或保存时发生错误.\n详细信息: {e}',icon='error')
                return
            
            #Up_Box(parent=Window_HexcolorToPixelImage,text='绘制完成',wait_time=6,after=True)
            MessageBox(parent=Window_HexcolorToPixelImage,title='信息',text='绘制完成.',icon='info')
            

    Button_draw_colors=ttk.Button(Window_HexcolorToPixelImage,text='导出',default='active',command=draw_colors)
    Button_draw_colors.place(x=600,y=450,width=80,height=30)
    Button_draw_colors.bind('<Return>',draw_colors)

    LinkLabel(Window_HexcolorToPixelImage,text='建议搭配渐变色计算器使用,点击进入.',anchor='w',url="https://photokit.com/colors/color-gradient/?lang=zh").place(x=20,y=450,width=300,height=30)

    Window_HexcolorToPixelImage.iconbitmap(f"{resource_path}icon.ico")
    Window_HexcolorToPixelImage.wait_window(Window_HexcolorToPixelImage)





def exit_app(event=None):
    root.destroy()
    sys.exit()
root=tk.Tk()
root.title('Modelbench-Tools ')
width=780
height=400
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(geometry)
root.resizable(0,0)
root.focus()
root.focus_force()



Frame_mbtools=tk.LabelFrame(root,text=lang('Modelbench工具集'),relief='solid',)
Frame_mbtools.place(x=20,y=10,width=360,height=290)

Button_func_MimodelResetTextureScale=ttk.Button(Frame_mbtools,text=lang('重置贴图纹理比例到1'),command=MimodelResetTextureScale)
Button_func_MimodelResetTextureScale.place(x=20,y=20,width=230,height=40)
TipsLabel(Frame_mbtools,text_tipswindow=lang('在不改变模型内容的前提下,将mimodel中某个贴图的纹理比例(如下如所示)重置为1,并相应调整UV坐标和方块尺寸,最终生成一个处理好的模型文件(不会生成贴图文件!).'),insert_picture_path=f'{resource_path}Tips2.png',icon='question').place(x=260,y=20,width=40,height=40)
TipsLabel(Frame_mbtools,text_color="#ff6600",text_tipswindow=lang('●一次只能对一张贴图进行处理,可对生成后的模型文件进行再次处理.'),icon='modern_warning').place(x=300,y=20,width=40,height=40)


Button_func_MimodelTextureMmergeTool=ttk.Button(Frame_mbtools,text=lang('贴图合并'),command=MimodelTextureMmerge)
Button_func_MimodelTextureMmergeTool.place(x=20,y=80,width=230,height=40)
TipsLabel(Frame_mbtools,text_tipswindow=lang('将一个模型中的所有贴图合并为一个贴图,最终生成一个模型文件和一个贴图文件.'),insert_picture_path=f'{resource_path}Tips3.png',icon='question').place(x=260,y=80,width=40,height=40)
TipsLabel(Frame_mbtools,text_color='#ff6600',text_tipswindow=lang('●贴图合并时需手动排布,并按下回车键确定.'),icon='modern_warning').place(x=300,y=80,width=40,height=40)


Button_func_MimodelUVSeparationAndFinishing=ttk.Button(Frame_mbtools,text=lang('UV分离与整理'),command=MimodelUVSeparationAndFinishing)
Button_func_MimodelUVSeparationAndFinishing.place(x=20,y=140,width=230,height=40)
TipsLabel(Frame_mbtools,text_tipswindow=lang('将杂乱无章的UV整理得井然有序(这在接单中比较有用,虽然没什么实际用处),最终生成一个模型文件和一个贴图文件.'),icon='question').place(x=260,y=140,width=40,height=40)
TipsLabel(Frame_mbtools,text_color='#ec1c24',text_tipswindow=lang('●仅接受纹理比例为1的单一贴图的模型文件.\n●不支持"混合材质"项.\n●新贴图宽高要合理,否则程序运行出错或缓慢.\n●建议保持勾选底部两个复选框,必须勾选右边的复选框,否则贴图在ModelBench中设定的透明度会失效(ModelBench不支持透明度纹理,亲测!).'),
          icon='stop').place(x=300,y=140,width=40,height=40)


Button_func_MimodelRenameRedDuplicateComponents=ttk.Button(Frame_mbtools,text=lang('重命名红色重名组件'),command=MimodelRenameRedDuplicateComponents)
Button_func_MimodelRenameRedDuplicateComponents.place(x=20,y=200,width=230,height=40)
TipsLabel(Frame_mbtools,text_tipswindow=lang('将ModelBench中红色的重名部件全部改名为不重名的名称,保证ModelBench与Mine-imator的名称一致性.'),icon='question').place(x=260,y=200,width=40,height=40)


Frame_bbtools=tk.LabelFrame(root,text=lang('Blockbench工具集'),relief='solid',)
Frame_bbtools.place(x=400,y=10,width=360,height=110)

Button_func_BBmodelFaceToBoxUV=ttk.Button(Frame_bbtools,text=lang('UV逐面转箱式'),command=BBmodelFaceToBoxUV)
Button_func_BBmodelFaceToBoxUV.place(x=20,y=20,width=230,height=40)

Frame_colortools=tk.LabelFrame(root,text=lang('颜色工具集'),relief='solid',)
Frame_colortools.place(x=400,y=140,width=360,height=120)
Button_func_HexcolorToPixelImage=ttk.Button(Frame_colortools,text=lang('多行颜色数值转像素图像\n&渐变色运算器'),command=HexcolorToPixelImage)
Button_func_HexcolorToPixelImage.place(x=20,y=20,width=230,height=50)
TipsLabel(Frame_colortools,text_tipswindow=lang('将多行颜色的十六进制值绘制为一个像素线条并作为文件生成.'),icon='question',insert_picture_path=f'{resource_path}Tips4.png').place(x=260,y=25,width=40,height=40)





def open_language_select_window():
    def press_enter(event=None):
        if Window_LanguageSettings.focus_get()==Button_cancel:
            close_Window_LanguageSettings()
        else:
            ok_languages_settings()
    def close_Window_LanguageSettings(event=None):
        root.attributes('-disabled', 'false')
        Window_LanguageSettings.destroy()
        root.focus()
    Window_LanguageSettings=tk.Toplevel(root)
    Window_LanguageSettings.title('语言设置 Language Settings')
    width=350
    height=160
    screenwidth = Window_LanguageSettings.winfo_screenwidth()
    screenheight = Window_LanguageSettings.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Window_LanguageSettings.geometry(geometry)
    Window_LanguageSettings.resizable(0,0)
    Window_LanguageSettings.protocol("WM_DELETE_WINDOW", close_Window_LanguageSettings)
    Window_LanguageSettings.bind('<Escape>',close_Window_LanguageSettings)
    root.attributes('-disabled', 'true')
    Window_LanguageSettings.wm_transient(root)
    Window_LanguageSettings.focus()
    Window_LanguageSettings.bind('<Return>',press_enter)

    tk.Label(Window_LanguageSettings,text='选择语言 Select Language:',anchor='w').place(x=20,y=20,width=300,height=20)

    Var_Combobox_language=tk.StringVar()
    Var_Combobox_language.set(CURRENT_LANGUAGE)
    Combobox_language=ttk.Combobox(Window_LanguageSettings,state='readonly',values=LANGUAGES_CODES,textvariable=Var_Combobox_language)
    Combobox_language.place(x=20,y=60,width=190,height=30)
    Combobox_language.focus()

    s=ttk.Style()
    s.configure('TButton',anchor='center')

    def refresh_LANGUAGE_CODES_and_Combobox():
        refresh_LANGUAGE_CODES()
        
        Combobox_language['values']=LANGUAGES_CODES
        Window_LanguageSettings.update()
    
    Button_refresh_languages_codes=ttk.Button(Window_LanguageSettings,text='',command=refresh_LANGUAGE_CODES_and_Combobox,style='TButton')
    Button_refresh_languages_codes.place(x=230,y=60,width=40,height=30)
    set_image(Button_refresh_languages_codes,"refresh.ico",[20,20])


    def open_language_folder():
        if os.path.exists("languages/") and os.path.isdir("languages/"):
            os.startfile(f"{os.getcwd()}/languages/")
        else:
            win32api.MessageBeep()
    Button_open_language_folder=ttk.Button(Window_LanguageSettings,text='',command=open_language_folder)
    Button_open_language_folder.place(x=290,y=60,width=40,height=30)
    set_image(Button_open_language_folder,"folder.ico",[20,20])

    def ok_languages_settings():
        global LANGUAGES,CURRENT_LANGUAGE
        original_current_language=CURRENT_LANGUAGE
        langcode=Var_Combobox_language.get()
        try:
            langfile=f"languages/{langcode}.json"
            with open(langfile,'r',encoding='utf-8') as f:
                data_language=json.load(f)
            with open("languages/language_settings.json",'w',encoding='utf-8') as f:
                json.dump({"current_language":langcode},f,indent=4,ensure_ascii=False)
            LANGUAGES[Var_Combobox_language.get()]=data_language
            CURRENT_LANGUAGE=langcode

            if langcode!=original_current_language:
                if MessageBox(parent=Window_LanguageSettings,text="语言设置已更改,是否重启软件以应用新的语言设置?\nThe language settings have been changed. Do you want to restart the software to apply the new language settings?",title='疑问',icon="question",buttonmode=2,text_true='✔',text_false='✘')==True:
                    root.destroy()
                    os.execl(sys.executable,sys.executable,*sys.argv)
                    sys.exit()
            close_Window_LanguageSettings()

        except Exception as e:
            MessageBox(parent=Window_LanguageSettings,text=f"加载语言文件出错,将使用默认语言包.\n详细信息: {e}",title='错误',icon="error")
            LANGUAGES=BACKUP_LANGUAGES
            CURRENT_LANGUAGE='ZH_CN'
            close_Window_LanguageSettings()
        
    def update_button_focus(event=None):
        if Window_LanguageSettings.focus_get() == Button_cancel:
            Button_ok['default'], Button_cancel['default'] = 'normal', 'active'
        else:
            Button_ok['default'], Button_cancel['default'] = 'active', 'normal'

    Button_ok = ttk.Button(Window_LanguageSettings, text="✔", command=ok_languages_settings, default='active')
    Button_ok.place(x=150, y=110, width=80, height=30)

    Button_cancel = ttk.Button(Window_LanguageSettings, text="✘", command=close_Window_LanguageSettings)
    Button_cancel.place(x=250, y=110, width=80, height=30)

    Button_ok.bind('<FocusIn>', update_button_focus)
    Button_ok.bind('<FocusOut>', update_button_focus)
    Button_cancel.bind('<FocusIn>', update_button_focus)
    Button_cancel.bind('<FocusOut>', update_button_focus)

    Window_LanguageSettings.iconbitmap(f"{resource_path}icon.ico")
    Window_LanguageSettings.wait_window(Window_LanguageSettings)


Button_Language=ttk.Button(root,text=' 语言 Language',command=open_language_select_window,compound='left')
Button_Language.place(x=580,y=330,width=180,height=50)
set_image(Button_Language,"language.ico",[36,36])




LinkLabel(root,text=lang('Github项目页'),anchor='w',url="https://github.com/zhatujianguanzhe/modelbench-tools").place(x=20,y=320,width=150,height=30)

LinkLabel(root,text=lang('Discord伺服器'),anchor='w',url='https://discord.gg/Ukr55F2Ypc').place(x=270,y=320,width=150,height=30)

tk.Label(root,text=lang('版本: 1.1.4          版权: Copyright © 2025-2030 炸图监管者'),anchor='w').place(x=20,y=360,width=470,height=30)


root.iconbitmap(f'{resource_path}icon.ico')

root.mainloop()
