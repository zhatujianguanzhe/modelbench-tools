import json
import sys,os,shutil
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from tkinter import filedialog
import win32api,win32con,ctypes
from PIL import Image,ImageTk
if getattr(sys, 'frozen', None):
    res_icon_folder = sys._MEIPASS.replace(r'\\','/').replace('\\',r'\\')+'/icons/'
    res_code_path=sys._MEIPASS.replace(r'\\','/').replace('\\',r'\\')+'/code/逐面2箱式.py'
else:
    res_icon_folder = os.path.dirname(__file__).replace(r'\\','/').replace('\\',r'\\')+'/icons/'
    res_code_path=os.path.dirname(__file__).replace(r'\\','/').replace('\\',r'\\')+'/逐面2箱式.py'
dont_warn_again=False
def Message_Box_Auto(parent=None, text='', title='', icon='none',text_true='确定',text_false='取消', buttonmode=1, defaultfocus=1,show_checkbutton=False):
    global dont_warn_again
    if dont_warn_again==True: return True
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
        s=ttk.Style()
        s.configure('Warning.TCheckbutton',anchor='w')
        Checkbutton_dont_warn=ttk.Checkbutton(Message_Box_window,text='保持选择,不再弹出.',style='Warning.TCheckbutton',onvalue=True,offvalue=False,variable=Var_dont_warn)
        Checkbutton_dont_warn.bind('<Return>',lambda e:Checkbutton_dont_warn.invoke())
        if show_checkbutton: Checkbutton_dont_warn.place(x=20,y=buttons_y,width=250,height=30)
        
        
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
    Message_Box_window.wm_iconbitmap(f"{res_icon_folder}/icon.ico")
    Message_Box_window.wait_window(Message_Box_window)

    if buttonmode==2:
        if Var_dont_warn.get()==True:
            dont_warn_again=True

    return rtn


def exit_app(event=None):
    root.destroy()
    sys.exit()
root=tk.Tk()
root.title('bbmodel逐面转箱式')
width=510
height=370
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(geometry)
root.resizable(0,0)
root.bind('<Escape>',exit_app)
root.focus()

tk.Label(root,text='原bb模型文件路径: ',anchor='w').place(x=20,y=20,width=170,height=30)
Entry_original_bbmodel_file=ttk.Entry(root,)
Entry_original_bbmodel_file.place(x=200,y=20,width=230,height=30)
def browse_original_bbmodel_file():
    file_path = filedialog.askopenfilename(filetypes=[("bbmodel文件", "*.bbmodel"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_original_bbmodel_file.delete(0, 'end')
        Entry_original_bbmodel_file.insert(0, file_path)
Button_browse_original_bbmodel_file=ttk.Button(root,text='...',command=browse_original_bbmodel_file)
Button_browse_original_bbmodel_file.place(x=450,y=20,width=40,height=30)


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


tk.Label(root,text='新bb模型文件路径: ',anchor='w').place(x=20,y=120,width=170,height=30)
Entry_new_bbmodel_file=ttk.Entry(root,)
Entry_new_bbmodel_file.place(x=200,y=120,width=230,height=30)
def browse_new_bbmodel_file():
    file_path = filedialog.asksaveasfilename(parent=root,defaultextension='.bbmodel',filetypes=[("bbmodel文件", "*.bbmodel"), ("所有文件", "*.*")])
    if file_path!='' and file_path!=None:
        Entry_new_bbmodel_file.delete(0, 'end')
        Entry_new_bbmodel_file.insert(0, file_path)
Button_browse_new_bbmodel_file=ttk.Button(root,text='...',command=browse_new_bbmodel_file)
Button_browse_new_bbmodel_file.place(x=450,y=120,width=40,height=30)


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

tk.Label(root,text='必须使用通用模型进行转换;逐面贴图不能拉伸.',anchor='w',fg="#C90000").place(x=20,y=320,width=370,height=30)



def start_convert(event=None):
    def is_pil_image_empty(img):
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        alpha = img.getchannel('A')
        return not alpha.getextrema()[1]  # 最大值为0则全透明

    if Entry_original_bbmodel_file.get().replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择原bb模型文件.',icon='error');Entry_original_bbmodel_file.focus_set();return
    if Entry_original_texture_file.get().replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择原贴图文件.',icon='error');Entry_original_texture_file.focus_set();return
    if Entry_new_bbmodel_file.get().replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择新bb模型文件.',icon='error');Entry_new_bbmodel_file.focus_set();return
    if Entry_new_texture_file.get().replace(' ','')=='': Message_Box_Auto(parent=root,title='错误',text='未选择新贴图文件.',icon='error');Entry_new_texture_file.focus_set();return
    if not os.path.exists(Entry_original_bbmodel_file.get()): Message_Box_Auto(parent=root,title='错误',text='原bb模型文件不存在.',icon='error');Entry_original_bbmodel_file.focus_set();return
    if not os.path.exists(Entry_original_texture_file.get()): Message_Box_Auto(parent=root,title='错误',text='原贴图文件不存在.',icon='error');Entry_original_texture_file.focus_set();return
    if os.path.exists(Entry_new_bbmodel_file.get()): Message_Box_Auto(parent=root,title='错误',text='新bb模型文件已存在.',icon='error');Entry_new_bbmodel_file.focus_set();return
    if os.path.exists(Entry_new_texture_file.get()): Message_Box_Auto(parent=root,title='错误',text='新贴图文件已存在.',icon='error');Entry_new_texture_file.focus_set();return

    try: int(Spinbox_new_texture_width.get())
    except: Message_Box_Auto(parent=root,title='错误',text='新贴图宽输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return
    try: int(Spinbox_new_texture_height.get())
    except: Message_Box_Auto(parent=root,title='错误',text='新贴图高输入错误.',icon='error');Spinbox_new_texture_width.focus_set();return

    try :
        with open(Entry_original_bbmodel_file.get(),'r',encoding='utf-8') as f:
            data_original_bbmodel = json.load(f)
    except Exception as e:
        Message_Box_Auto(parent=root,title='错误',text='原bb模型文件读取或解析失败.\n详细信息: '+str(e),icon='error')
        Entry_original_bbmodel_file.focus_set()
        return
    
    if data_original_bbmodel['meta']['box_uv']==True:
        Message_Box_Auto(parent=root,title='错误',text='原bb模型文件不是逐面UV.',icon='error')
        Entry_original_bbmodel_file.focus_set()
        return

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

        for face_name, face_data in i['faces'].items():
            #face_name指的是朝向而非名字
            face_size=(face_data['uv'][2]-face_data['uv'][0],face_data['uv'][3]-face_data['uv'][1])
            if face_name=='north':
                if face_size[0]!=block_size[0] or face_size[1]!=block_size[1]:
                    if Message_Box_Auto(parent=root,title='警告',text='方块 '+block_name+' 的 north 面出现拉伸错误,会导致贴图错误.',buttonmode=2,defaultfocus=1,show_checkbutton=True,icon='warning',text_true='忽略',text_false='终止')==False:
                        return
            
            elif face_name=='south':
                if face_size[0]!=block_size[0] or face_size[1]!=block_size[1]:
                    if Message_Box_Auto(parent=root,title='警告',text='方块 '+block_name+' 的 south 面出现拉伸错误,会导致贴图错误.',buttonmode=2,defaultfocus=1,show_checkbutton=True,icon='warning',text_true='忽略',text_false='终止')==False:
                        return
            elif face_name=='east':
                if face_size[0]!=block_size[2] or face_size[1]!=block_size[1]:
                    if Message_Box_Auto(parent=root,title='警告',text='方块 '+block_name+' 的 east 面出现拉伸错误,会导致贴图错误.',buttonmode=2,defaultfocus=1,show_checkbutton=True,icon='warning',text_true='忽略',text_false='终止')==False:
                        return
            elif face_name=='west':
                if face_size[0]!=block_size[2] or face_size[1]!=block_size[1]:
                    if Message_Box_Auto(parent=root,title='警告',text='方块 '+block_name+' 的 west 面出现拉伸错误,会导致贴图错误.',buttonmode=2,defaultfocus=1,show_checkbutton=True,icon='warning',text_true='忽略',text_false='终止')==False:
                        return
            elif face_name=='up':
                if abs(face_size[0])!=block_size[0] or abs(face_size[1])!=block_size[2]:
                    if Message_Box_Auto(parent=root,title='警告',text='方块 '+block_name+' 的 up 面出现拉伸错误,会导致贴图错误.',buttonmode=2,defaultfocus=1,show_checkbutton=True,icon='warning',text_true='忽略',text_false='终止')==False:
                        return
            elif face_name=='down':
                if abs(face_size[0])!=block_size[0] or abs(face_size[1])!=block_size[2]:
                    if Message_Box_Auto(parent=root,title='警告',text='方块 '+block_name+' 的 down 面出现拉伸错误,会导致贴图错误.',buttonmode=2,defaultfocus=1,show_checkbutton=True,icon='warning',text_true='忽略',text_false='终止')==False:
                        return

    #检查结束
    #数据转换开始
    pil_original_texture=Image.open(Entry_original_texture_file.get()).convert('RGBA')
    pil_new_texture = Image.new('RGBA', (int(Spinbox_new_texture_width.get()),int(Spinbox_new_texture_height.get())), (0, 0, 0, 0))

    # 遍历所有元素
    """
    for idx, element in enumerate(data_original_bbmodel['elements']):
        block_size = (
            int(element['to'][0] - element['from'][0]),
            int(element['to'][1] - element['from'][1]),
            int(element['to'][2] - element['from'][2]),
        )
        block_name = element['name']

        face_relative_pos_dict = {}  # 存储每个面的相对位置

        # 在此处添加功能.根据blockbench的通用模型,计算出每个面的相对位置
        # Blockbench标准UV布局：前面、后面、左面、右面、上面、下面
        # 计算每个面的相对位置，以贴图左上角为原点(0,0)
        face_width = block_size[0]  # x轴长度
        face_height = block_size[1]  # y轴长度
        face_depth = block_size[2]  # z轴长度

        box_uv_height = face_height + face_depth
        row_max_height = max(row_max_height, box_uv_height)

        # 根据Blockbench标准布局计算每个面的相对位置
        # 前面(north)位于中间，宽度为x轴长度，高度为y轴长度
        face_relative_pos_dict['north'] = (face_depth, face_depth, face_width, face_height)
        # 后面(south)位于最右侧，宽度为x轴长度，高度为y轴长度
        face_relative_pos_dict['south'] = (face_depth * 2 + face_width, face_depth, face_width, face_height)
        # 左面(west)位于最左侧，宽度为z轴长度，高度为y轴长度
        face_relative_pos_dict['west'] = (0, face_depth, face_depth, face_height)
        # 右面(east)位于中间右侧，宽度为z轴长度，高度为y轴长度
        face_relative_pos_dict['east'] = (face_depth + face_width, face_depth, face_depth, face_height)
        # 上面(up)位于中间上方，宽度为x轴长度，高度为z轴长度
        face_relative_pos_dict['up'] = (face_depth, 0, face_width, face_depth)
        # 下面(down)位于中间下方，宽度为x轴长度，高度为z轴长度
        face_relative_pos_dict['down'] = (face_depth + face_width, 0, face_width, face_depth)

        # 打印每个面的相对位置信息
        #print(f"方块 {block_name} 的面相对位置:")

        #for face, pos in face_relative_pos_dict.items():
        #    print(f"{face}: (x={pos[0]}, y={pos[1]}, 宽={pos[2]}, 高={pos[3]})")

        # 图片处理
    # offset_for_uv_x=0
        for side in ['north', 'south', 'west', 'east', 'up', 'down']:
            # 获取原始UV坐标
            original_uv = element['faces'][side]['uv']

            # 使用原始UV坐标裁剪图像
            #注意:顶底部是反过来的,是负的,所以要预处理
            #if side in ['up','down']:
            original_uv = change_(original_uv)
            temp_picture = pil_original_texture.crop((
                original_uv[0],
                original_uv[1],
                original_uv[2],
                original_uv[3],
            ))
                
            # 计算新位置，考虑偏移量
            new_x = face_relative_pos_dict[side][0] + offset_x 
            new_y = face_relative_pos_dict[side][1] + offset_y 
            
            # 将裁剪的图像粘贴到新位置
            pil_new_texture.paste(temp_picture, (new_x, new_y))
            
            # 更新模型中的UV坐标
            data_original_bbmodel['elements'][idx]['faces'][side]['uv'] = [
                new_x,
                new_y,
                new_x + face_relative_pos_dict[side][2],
                new_y + face_relative_pos_dict[side][3]
            ]
            data_original_bbmodel['elements'][idx]['box_uv'] = True  # 设置 box_uv 为 True
            data_original_bbmodel['elements'][idx]['uv_offset']=[offset_x,offset_y]
    
        # 更新偏移量，为下一个方块准备位置
        # Blockbench标准布局中，方块的总宽度是 face_depth*2 + face_width*2
        # 总高度是 face_height + face_depth
        print(offset_x + face_depth*2 + face_width*2,pil_new_texture.size[0])
        if offset_x + face_depth*2 + face_width*2 > pil_new_texture.size[0]:
            # 如果当前行空间不足，换到下一行
            offset_x = 0
            #offset_y += int(max(face_height, face_depth) * 3)#*修改这里   # 确保高度足够容纳所有面
            #使用二分法确定可用的y位置
            

                        # 使用新的换行逻辑
            offset_y += row_max_height
            row_max_height = 0
            '''
            pil_binari_search_texture=Image.new('RGBA',(pil_new_texture.size[0],1))
            while True:
                # 二分法查找最小的全透明行 y
                low, high = 0, pil_new_texture.size[1] - 1
                ans = pil_new_texture.size[1]
                while low <= high:
                    mid = (low + high) // 2
                    pil_binari_search_texture.paste(
                        pil_new_texture.crop((0, mid, pil_new_texture.size[0], mid + 1)),
                        (0, 0)
                    )
                    if is_pil_image_empty(pil_binari_search_texture):
                        ans = mid
                        high = mid - 1
                    else:
                        low = mid + 1
                offset_y = ans
                break
            '''
        else:
            # 当前行还有空间，继续向右排列
            offset_x += face_depth*2 + face_width*2 
        
        # 检查是否超出画布高度
        if offset_y > int(Spinbox_new_texture_height.get()):
            Message_Box_Auto(parent=root,title='错误',text='贴图空间不足,需增加贴图尺寸.',icon='error')
            Spinbox_new_texture_height.focus_set()
            return
    """

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
        Message_Box_Auto(parent=root,title='错误',text='新bb模型文件写入失败.\n详细信息: '+str(e),icon='error')
        Entry_new_bbmodel_file.focus_set()
        return
    try:
        pil_new_texture.save(Entry_new_texture_file.get())
    except Exception as e:
        Message_Box_Auto(parent=root,title='错误',text='新贴图文件写入失败.\n详细信息: '+str(e),icon='error')
        Entry_new_texture_file.focus_set()
        return
   
    Message_Box_Auto(parent=root,title='信息',text='模型UV模式转换完成.',icon='info')


root.bind('<Return>',start_convert)
Button_start=ttk.Button(root,text='开始转换',default='active',command=start_convert)
Button_start.place(x=410,y=320,width=80,height=30)



Button_infos=ttk.Button(root,text='关于',takefocus=False,command=lambda: Message_Box_Auto(parent=root,title='关于',text='Copyright ©2025 炸图监管者 All rights reserved.\n本程序遵循 GNU AGPL v3 开源协议.详情参见https://www.gnu.org/licenses/agpl-3.0.html',icon='info'))
Button_infos.place(x=320,y=220,width=70,height=30)

Button_no_dpi=ttk.Button(root,text='清晰界面',takefocus=False,command=lambda: ctypes.windll.shcore.SetProcessDpiAwareness(1))
Button_no_dpi.place(x=320,y=270,width=70,height=30)


Button_download_code=ttk.Button(root,text='问题反馈',command=lambda: Message_Box_Auto(parent=root,title='问题反馈',text='E-mail: 1323738778@qq.com',icon='info'),takefocus=False)
Button_download_code.place(x=410,y=220,width=80,height=30)


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
    #shutil.copy(res_code_path,
Button_download_code=ttk.Button(root,text='保存源码',command=download_code,takefocus=False)
Button_download_code.place(x=410,y=270,width=80,height=30)




root.iconbitmap(f"{res_icon_folder}icon.ico")
root.mainloop()

