#现在已不再更新这个文件,请转向Modelbench-Tools.py
import json,math,pyperclip
import sys,os,shutil
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from tkinter import filedialog
import win32api,win32con,ctypes,webbrowser
from PIL import Image,ImageTk,ImageDraw,ImageColor

if getattr(sys, 'frozen', None):
    res_icon_folder = sys._MEIPASS.replace(r'\\','/').replace('\\',r'\\')+'/icons/'
    res_code_path=sys._MEIPASS.replace(r'\\','/').replace('\\',r'\\')+'/code/mimodel分离与整理.py'
else:
    res_icon_folder = os.path.dirname(__file__).replace(r'\\','/').replace('\\',r'\\')+'/icons/'
    res_code_path=os.path.dirname(__file__).replace(r'\\','/').replace('\\',r'\\')+'/mimodel分离与整理.py'

def Message_Box_Auto(parent=None, text='', title='', icon='none',text_true='确定',text_false='取消', buttonmode=1, defaultfocus=1):

    # --- 辅助函数：更精确地计算文本高度（改进版）---
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
        set_image(label_icon, f"{res_icon_folder}/{icon}.ico", img_size=(45, 45))

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

        Var_dont_warn=tk.BooleanVar()
        Var_dont_warn.set(True)
        Checkbutton_dont_warn=ttk.Checkbutton(Message_Box_window,text='保持选择,不再弹出.',style='Warning.TCheckbutton',onvalue=True,offvalue=False,variable=Var_dont_warn)
        Checkbutton_dont_warn.bind('<Return>',lambda e:Checkbutton_dont_warn.invoke())
        
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
        'question': win32con.MB_ICONQUESTION, 'safe_question': win32con.MB_ICONQUESTION,
        'error': win32con.MB_ICONERROR, 'modern_error': win32con.MB_ICONERROR,
        'safe_error': win32con.MB_ICONERROR, 'word_error_red': win32con.MB_ICONERROR,
        'word_deny': win32con.MB_ICONERROR, 'warning': win32con.MB_ICONWARNING,
        'safe_warning': win32con.MB_ICONWARNING, 'word_correct_orange': win32con.MB_ICONWARNING,
        'modern_warning': win32con.MB_ICONWARNING, 'uac': win32con.MB_ICONWARNING,
        'info': win32con.MB_ICONINFORMATION, 'word_correct_green': win32con.MB_ICONINFORMATION,
        'safe_correct': win32con.MB_ICONINFORMATION, 'modern_correct': win32con.MB_ICONINFORMATION,
        'modern_correct_gray': win32con.MB_ICONINFORMATION, 'none': 0
    }

    win32api.MessageBeep(beep_map.get(icon, 0))
    Message_Box_window.wm_iconbitmap(f"{res_icon_folder}icon.ico")
    Message_Box_window.wait_window(Message_Box_window)
    return rtn






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
        # 在这里对 shape 进行操作
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

    

def main_run(event=None):
    global img_old,img_new,offset_x,offset_y,row_max_height,new_mimodel_file,new_texture_file,new_texture_width,new_texture_height
    original_mimodel_file=Entry_original_mimodel_file.get().strip().replace('\\','/')
    original_texture_file=Entry_original_texture_file.get().strip().replace('\\','/')
    new_mimodel_file=Entry_new_mimodel_file.get().strip().replace('\\','/')
    new_texture_file=Entry_new_texture_file.get().strip().replace('\\','/')
    
    if original_mimodel_file.replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择原mimodel文件.',icon='error');Entry_original_mimodel_file.focus_set();return
    if original_texture_file.replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择原贴图文件.',icon='error');Entry_original_texture_file.focus_set();return
    if new_mimodel_file.replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择新mimodel文件.',icon='error');Entry_new_mimodel_file.focus_set();return
    if new_texture_file.replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择新贴图文件.',icon='error');Entry_new_texture_file.focus_set();return
    if not os.path.exists(original_mimodel_file): Message_Box_Auto(parent=root,title='错误',text='原mimodel文件不存在.',icon='error');Entry_original_mimodel_file.focus_set();return
    if not os.path.exists(original_texture_file): Message_Box_Auto(parent=root,title='错误',text='原贴图文件不存在.',icon='error');Entry_original_texture_file.focus_set();return
    if os.path.exists(new_mimodel_file): Message_Box_Auto(parent=root,title='错误',text='新mimodel型文件已存在.',icon='error');Entry_new_mimodel_file.focus_set();return
    if os.path.exists(new_texture_file): Message_Box_Auto(parent=root,title='错误',text='新贴图文件已存在.',icon='error');Entry_new_texture_file.focus_set();return

    try: new_texture_width=int(Spinbox_new_texture_width.get())
    except: Message_Box_Auto(parent=root,title='错误',text='新贴图宽输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return
    try: new_texture_height=int(Spinbox_new_texture_height.get())
    except: Message_Box_Auto(parent=root,title='错误',text='新贴图高输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return

    for child in root.winfo_children():
        if child.winfo_class()=='TButton':
            child.config(state='disabled')
        elif child.winfo_class()=='TSpinbox' or child.winfo_class()=='TEntry':
            child.config(state='readonly')
    root.update()

    try:
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
                Message_Box_Auto(parent=root,title='错误',text='新贴图尺寸不足,无法继续排布.',icon='error')
                return
        
        with open(new_mimodel_file,'w',encoding='utf-8') as f:
            f.write(json.dumps(data_mimodel, indent=4,ensure_ascii=False))
        Message_Box_Auto(parent=root,title='信息',text='处理完成.',icon='info')
    except Exception as e:
        Message_Box_Auto(parent=root,title='错误',text='处理文件时发生错误.\n详细信息: '+str(e),icon='error')
        return
    finally:
        for child in root.winfo_children():
            if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                child.config(state='normal')
        root.update()
    


def exit_app(event=None):
    root.destroy()
    sys.exit()
root=tk.Tk()
root.title('mimodelUV分离与整理')
width=510
height=420
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(geometry)
root.resizable(0,0)
root.bind('<Escape>',exit_app)
root.focus()

tk.Label(root,text='仅支持单贴图,多贴图需先使用我的工具转换.不支持"混合材质"项.',anchor='w',fg="#C90000").place(x=20,y=320,width=470,height=30)


tk.Label(root,text='原mimodel文件路径: ',anchor='w').place(x=20,y=20,width=170,height=30)
Entry_original_mimodel_file=ttk.Entry(root,)
Entry_original_mimodel_file.place(x=200,y=20,width=230,height=30)
def browse_original_mimodel_file():
    file_path = filedialog.askopenfilename(filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_original_mimodel_file.delete(0, 'end')
        Entry_original_mimodel_file.insert(0, file_path)
Button_browse_original_mimodel_file=ttk.Button(root,text='...',command=browse_original_mimodel_file)
Button_browse_original_mimodel_file.place(x=450,y=20,width=40,height=30)



tk.Label(root,text='原贴图文件路径: ',anchor='w').place(x=20,y=70,width=170,height=30)
Entry_original_texture_file=ttk.Entry(root,)
Entry_original_texture_file.place(x=200,y=70,width=230,height=30)
def browse_original_texture_file():
    file_path = filedialog.askopenfilename(filetypes=[("png文件", "*.png"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_original_texture_file.delete(0, 'end')
        Entry_original_texture_file.insert(0, file_path)
Button_browse_original_texture_file=ttk.Button(root,text='...',command=browse_original_texture_file)
Button_browse_original_texture_file.place(x=450,y=70,width=40,height=30)


tk.Label(root,text='新mimodel文件路径: ',anchor='w').place(x=20,y=120,width=170,height=30)
Entry_new_mimodel_file=ttk.Entry(root,)
Entry_new_mimodel_file.place(x=200,y=120,width=230,height=30)
def browse_new_mimodel_file():
    file_path = filedialog.asksaveasfilename(parent=root,defaultextension='.mimodel',filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_new_mimodel_file.delete(0, 'end')
        Entry_new_mimodel_file.insert(0, file_path)
Button_browse_new_mimodel_file=ttk.Button(root,text='...',command=browse_new_mimodel_file)
Button_browse_new_mimodel_file.place(x=450,y=120,width=40,height=30)


tk.Label(root,text='新贴图文件路径: ',anchor='w').place(x=20,y=170,width=170,height=30)
Entry_new_texture_file=ttk.Entry(root,)
Entry_new_texture_file.place(x=200,y=170,width=230,height=30)
def browse_new_texture_file():
    file_path = filedialog.asksaveasfilename(parent=root,defaultextension='.png',filetypes=[("png文件", "*.png"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_new_texture_file.delete(0, 'end')
        Entry_new_texture_file.insert(0, file_path)
Button_browse_new_texture_file=ttk.Button(root,text='...',command=browse_new_texture_file)
Button_browse_new_texture_file.place(x=450,y=170,width=40,height=30)



tk.Label(root,text='新贴图宽:',anchor='w').place(x=20,y=220,width=120,height=30)
Spinbox_new_texture_width=ttk.Spinbox(root,from_=16,to=float('inf'),increment=16)
Spinbox_new_texture_width.place(x=200,y=220,width=100,height=30)
Spinbox_new_texture_width.insert(0,256)

tk.Label(root,text='新贴图高:',anchor='w').place(x=20,y=270,width=120,height=30)
Spinbox_new_texture_height=ttk.Spinbox(root,from_=16,to=float('inf'),increment=16)
Spinbox_new_texture_height.place(x=200,y=270,width=100,height=30)
Spinbox_new_texture_height.insert(0,256)

def show_about():
    #pyperclip.copy(r"https://drive.google.com/drive/folders/1jY9AA1xWP7xYr5TWWT6LXNY2peWHUKCN?usp=drive_link")
    #Message_Box_Auto(parent=root,title='关于',text='Copyright ©2025 炸图监管者 All rights reserved.\n本程序遵循GNU AGPL v3开源协议.\n详情参见: https://www.gnu.org/licenses/agpl-3.0.html\n最新下载链接已复制到剪切板.',icon='info')
    webbrowser.open('https://github.com/zhatujianguanzhe/modelbench-tools')
    
Button_infos=ttk.Button(root,text='Github',takefocus=False,command=show_about)
Button_infos.place(x=320,y=220,width=70,height=30)


def open_feedback():
    pyperclip.copy(r"https://discord.gg/ySJcpmFCVa")
    Message_Box_Auto(parent=root,title='问题反馈',text='E-mail: 1323738778@QQ.com\nDiscord频道已复制到剪切板.',icon='info')
Button_download_code=ttk.Button(root,text='问题反馈',command=open_feedback,takefocus=False)
Button_download_code.place(x=410,y=220,width=80,height=30)

Button_no_dpi=ttk.Button(root,text='清晰界面',takefocus=False,command=lambda: ctypes.windll.shcore.SetProcessDpiAwareness(1))
Button_no_dpi.place(x=320,y=270,width=70,height=30)


def download_code():
    new_code_path=filedialog.askdirectory(title='选择保存源码的位置',parent=root,)
    
    if new_code_path!='' and new_code_path!=None:
        try:
            shutil.copy(res_code_path,new_code_path)
            shutil.copytree(res_icon_folder,new_code_path+'/icons',)
        except Exception as e:
            print(e)
            Message_Box_Auto(parent=root,title='错误',text='源码保存失败.\n需要注意的是,此目录下不允许出现名为 icons 的文件或文件夹.\n详细信息: '+str(e),icon='error')
            return
        Message_Box_Auto(parent=root,title='信息',text='源码保存成功.',icon='info')

Button_download_code=ttk.Button(root,text='保存源码',command=download_code,takefocus=False)
Button_download_code.place(x=410,y=270,width=80,height=30)


def update_checkbutton(event=None):
    if Var_not_reset_color_settings.get()==True:
        Var_not_reset_alpha_settings.set(True)
        Checkbutton_not_reset_alpha_settings.config(state='disabled')
    else:
        Checkbutton_not_reset_alpha_settings.config(state='normal')

ttk.Style().configure('NOT.TCheckbutton',anchor='w')
Var_not_reset_color_settings=tk.BooleanVar()
Var_not_reset_color_settings.set(False)
Checkbutton_not_reset_color_settings=ttk.Checkbutton(root,text='保留MB颜色属性.',command=update_checkbutton,variable=Var_not_reset_color_settings,style='NOT.TCheckbutton',onvalue=True,offvalue=False)
Checkbutton_not_reset_color_settings.place(x=20,y=370,width=150,height=30)


Var_not_reset_alpha_settings=tk.BooleanVar()
Var_not_reset_alpha_settings.set(True)
Checkbutton_not_reset_alpha_settings=ttk.Checkbutton(root,text='保留MB透明度属性(推荐).',command=update_checkbutton,variable=Var_not_reset_alpha_settings,style='NOT.TCheckbutton',onvalue=True,offvalue=False)
Checkbutton_not_reset_alpha_settings.place(x=190,y=370,width=200,height=30)

root.bind('<Return>',main_run)
Button_start=ttk.Button(root,text='开始',default='active',command=main_run)
Button_start.place(x=410,y=370,width=80,height=30)


root.iconbitmap(res_icon_folder+'icon.ico')

root.mainloop()
