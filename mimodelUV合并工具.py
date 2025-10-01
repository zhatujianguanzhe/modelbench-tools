import json,pyperclip
import sys,os,shutil
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from tkinter import filedialog
import win32api,win32con,ctypes,webbrowser
from PIL import Image,ImageTk,ImageDraw,ImageColor

if getattr(sys, 'frozen', None):
    res_icon_folder = sys._MEIPASS.replace(r'\\','/').replace('\\',r'\\')+'/icons/'
    res_code_path=sys._MEIPASS.replace(r'\\','/').replace('\\',r'\\')+'/code/mimodelUV合并工具.py'
else:
    res_icon_folder = os.path.dirname(__file__).replace(r'\\','/').replace('\\',r'\\')+'/icons/'
    res_code_path=os.path.dirname(__file__).replace(r'\\','/').replace('\\',r'\\')+'/mimodelUV合并工具.py'

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


def Input_Box_Auto(title='', text='', parent=None, default='', canspace=True, canempty=False):
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

    Input_Box_Auto_window.wm_iconbitmap(f"{res_icon_folder}/icon.ico")
    Input_Box_Auto_window.wait_window(Input_Box_Auto_window)

    return rt



all_texture_dict={}
"""
def traverse_parts_shapes_set_temp_texture_key(data,parent_texture=None,):
    global all_texture_dict
    # 递归遍历所有 part
    # 优先使用当前 data 的 texture，否则用父级传递下来的 parent_texture
    current_texture = data.get('texture', parent_texture)

    # 处理当前part的shapes
    if "shapes" in data :
        if  isinstance(data["shapes"], list):
            shapes = data['shapes']
            for i, shape in enumerate(data["shapes"]):
            #for shape in data["shapes"]:
                shape['temp_texture'] = current_texture
                if current_texture not in all_texture_dict:
                    all_texture_dict[current_texture]=None

            shapes[i] = shape  # 写回原数据

    if "parts" in data and isinstance(data["parts"], list):
        parts = data['parts']
        for i, subpart in enumerate(data["parts"]):
            subpart['temp_texture'] = current_texture
            if current_texture not in all_texture_dict:
                all_texture_dict[current_texture]=None
             
        parts[i] = subpart  # 写回原数据
        traverse_parts_shapes_set_temp_texture_key(subpart, parent_texture=current_texture,)  # 递归处理子 part
    return all_texture_dict
"""
def traverse_parts_shapes_set_temp_texture_key(data, parent_texture=None):
    global all_texture_dict
    current_texture = data.get('texture', parent_texture)
    
    if "shapes" in data and isinstance(data["shapes"], list):
        shapes = data['shapes']
        for i, shape in enumerate(data["shapes"]):
            # 确保shape有texture属性
            if 'texture' not in shape:
                #shape['texture'] = current_texture
                shape['temp_texture'] = current_texture
            if current_texture not in all_texture_dict:
                all_texture_dict[current_texture] = None
            shapes[i] = shape
    
    if "parts" in data and isinstance(data["parts"], list):
        parts = data['parts']
        for i, subpart in enumerate(data["parts"]):
            if 'texture' not in subpart:
             #   subpart['texture'] = current_texture
                subpart['temp_texture'] = current_texture
            if current_texture not in all_texture_dict:
                all_texture_dict[current_texture] = None
            parts[i] = subpart
            traverse_parts_shapes_set_temp_texture_key(subpart, parent_texture=current_texture)
    return all_texture_dict       


def traverse_shapes_set_uv_offset(part):
    global all_texture_offset_dict,new_texture_img
    # 如果有 shapes 列表，处理它
    if 'shapes' in part and isinstance(part['shapes'], list):
        shapes = part['shapes']
        for i, shape in enumerate(shapes):

            shape['uv']=[shape['uv'][0]+all_texture_offset_dict[shape['temp_texture'] if 'texture' not in shape else shape['texture']][0],
                         shape['uv'][1]]
        new_shape = shape  
        shapes[i] = new_shape  # 写回原数据

    # 如果有子 parts，递归处理
    if 'parts' in part and isinstance(part['parts'], list):
        for subpart in part['parts']:
            traverse_shapes_set_uv_offset(subpart)

def traverse_parts_delete_texture_key(part):
  
    # 如果有子 parts，递归处理
    if 'parts' in part and isinstance(part['parts'], list):
        parts=part['parts']
        for i, subpart in enumerate(parts):
            if 'texture' in subpart:
                del subpart['texture']
            parts[i] = subpart  # 写回原数据
            traverse_parts_delete_texture_key(subpart)

def main_run(event=None):
    global all_texture_dict,all_texture_offset_dict,new_texture_img
    all_texture_dict={}
    all_texture_offset_dict={}

    original_mimodel_file=Entry_original_mimodel_file.get().strip().replace('\\','/')

    new_mimodel_file=Entry_new_mimodel_file.get().strip().replace('\\','/')
    new_texture_file=Entry_new_texture_file.get().strip().replace('\\','/')
    
    if original_mimodel_file.replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择原mimodel文件.',icon='error');Entry_original_mimodel_file.focus_set();return
    
    if new_mimodel_file.replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择新mimodel文件.',icon='error');Entry_new_mimodel_file.focus_set();return
    if new_texture_file.replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择新贴图文件.',icon='error');Entry_new_texture_file.focus_set();return
    if not os.path.exists(original_mimodel_file): Message_Box_Auto(parent=root,title='错误',text='原mimodel文件不存在.',icon='error');Entry_original_mimodel_file.focus_set();return
    
    if os.path.exists(new_mimodel_file): Message_Box_Auto(parent=root,title='错误',text='新mimodel型文件已存在.',icon='error');Entry_new_mimodel_file.focus_set();return
    if os.path.exists(new_texture_file): Message_Box_Auto(parent=root,title='错误',text='新贴图文件已存在.',icon='error');Entry_new_texture_file.focus_set();return
    try:
        for child in root.winfo_children():
            if child.winfo_class()=='TButton':
                child.config(state='disabled')
            elif child.winfo_class()=='TSpinbox' or child.winfo_class()=='TEntry':
                child.config(state='readonly')
        root.update()

        with open(original_mimodel_file,'r',encoding='utf-8') as f:
            data_mimodel=json.loads(f.read())


        traverse_parts_shapes_set_temp_texture_key(data_mimodel) #为每个part设置好临时材质键值




        for key in all_texture_dict.keys():

            temp_file=Input_Box_Auto(title='链接 '+key+' 的文件',text='文件:',parent=root,default=os.path.dirname(original_mimodel_file)+'/'+key,canspace=True,canempty=False).replace('\\','/')
            if temp_file==None or temp_file.replace(' ','')=='':
                Message_Box_Auto(parent=root,title='错误',text='必须链接材质文件.',icon='error')
                for child in root.winfo_children():
                        if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                            child.config(state='normal')
                root.update()
                return
            if not os.path.exists(temp_file):
                Message_Box_Auto(parent=root,title='错误',text='链接的材质文件不存在.',icon='error')
                for child in root.winfo_children():
                        if child.winfo_class() in ('TSpinbox', 'TEntry', 'TButton'):
                            child.config(state='normal')
                root.update()
                return

            all_texture_dict[key]=temp_file


        new_texture_size=[0,0]
        for key in all_texture_dict:
            temp_img=Image.open(all_texture_dict[key]).convert('RGBA')
            new_texture_size[0]+=temp_img.width
            new_texture_size[1]=max(new_texture_size[1],temp_img.height)
        
        new_texture_img=Image.new('RGBA', (new_texture_size[0] ,new_texture_size[1]), (0, 0, 0, 0))
        general_offset_x=0
        for key in all_texture_dict:#字典有序
            temp_img=Image.open(all_texture_dict[key]).convert('RGBA')
            new_texture_img.paste(temp_img,(general_offset_x,0))
            all_texture_offset_dict[key]=[general_offset_x,general_offset_x+temp_img.width-1]
            general_offset_x+=temp_img.width


        for part in data_mimodel.get('parts', []):
            traverse_shapes_set_uv_offset(part)
        for part in data_mimodel.get('parts', []):
            traverse_parts_delete_texture_key(part)
    
        with open(new_mimodel_file,'w',encoding='utf-8') as f:
            f.write(json.dumps(data_mimodel, indent=4,ensure_ascii=False))

        new_texture_img.save(new_texture_file)


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
root.title('mimodelUV合并工具')
width=510
height=320
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(geometry)
root.resizable(0,0)
root.bind('<Escape>',exit_app)
root.focus()

tk.Label(root,text='顶层part可能出现贴图设定错误,手动修改即可.',anchor='w',fg="#C90000").place(x=20,y=270,width=380,height=30)


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



tk.Label(root,text='新mimodel文件路径: ',anchor='w').place(x=20,y=70,width=170,height=30)
Entry_new_mimodel_file=ttk.Entry(root,)
Entry_new_mimodel_file.place(x=200,y=70,width=230,height=30)
def browse_new_mimodel_file():
    file_path = filedialog.asksaveasfilename(parent=root,defaultextension='.mimodel',filetypes=[("mimodel文件", "*.mimodel"), ("JSON文件", "*.json"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_new_mimodel_file.delete(0, 'end')
        Entry_new_mimodel_file.insert(0, file_path)
Button_browse_new_mimodel_file=ttk.Button(root,text='...',command=browse_new_mimodel_file)
Button_browse_new_mimodel_file.place(x=450,y=70,width=40,height=30)


tk.Label(root,text='新贴图文件路径: ',anchor='w').place(x=20,y=120,width=170,height=30)
Entry_new_texture_file=ttk.Entry(root,)
Entry_new_texture_file.place(x=200,y=120,width=230,height=30)
def browse_new_texture_file():
    file_path = filedialog.asksaveasfilename(parent=root,defaultextension='.png',filetypes=[("png文件", "*.png"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_new_texture_file.delete(0, 'end')
        Entry_new_texture_file.insert(0, file_path)
Button_browse_new_texture_file=ttk.Button(root,text='...',command=browse_new_texture_file)
Button_browse_new_texture_file.place(x=450,y=120,width=40,height=30)



def show_about():
    #pyperclip.copy(r"https://drive.google.com/drive/folders/1jY9AA1xWP7xYr5TWWT6LXNY2peWHUKCN?usp=drive_link")
    #Message_Box_Auto(parent=root,title='关于',text='Copyright ©2025 炸图监管者 All rights reserved.\n本程序遵循GNU AGPL v3开源协议.\n详情参见: https://www.gnu.org/licenses/agpl-3.0.html\n最新下载链接已复制到剪切板.',icon='info')
    webbrowser.open('https://github.com/zhatujianguanzhe/modelbench-tools')
    
Button_infos=ttk.Button(root,text='Github',takefocus=False,command=show_about)
Button_infos.place(x=320,y=170,width=70,height=30)


def open_feedback():
    pyperclip.copy(r"https://discord.gg/ySJcpmFCVa")
    Message_Box_Auto(parent=root,title='问题反馈',text='E-mail: 1323738778@QQ.com\nDiscord频道已复制到剪切板.',icon='info')
Button_download_code=ttk.Button(root,text='问题反馈',command=open_feedback,takefocus=False)
Button_download_code.place(x=410,y=170,width=80,height=30)

Button_no_dpi=ttk.Button(root,text='清晰界面',takefocus=False,command=lambda: ctypes.windll.shcore.SetProcessDpiAwareness(1))
Button_no_dpi.place(x=320,y=220,width=70,height=30)


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
Button_download_code.place(x=410,y=220,width=80,height=30)


root.bind('<Return>',main_run)
Button_start=ttk.Button(root,text='开始',default='active',command=main_run)
Button_start.place(x=410,y=270,width=80,height=30)


root.iconbitmap(res_icon_folder+'icon.ico')
root.mainloop()