import json
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from trip import run_script
import webview


def display_html_file():
    webview.create_window("Route Map", "./route_map.html", width=800, height=600)
    webview.start()


def run_script_and_enable_button(start_entry, end_entry, result_textbox, view_route_button):
    run_script(start_entry, end_entry, result_textbox)
    view_route_button.configure(state=tk.NORMAL)


def update_suggestions_start(event):
    typed_text = event.widget.get()
    if typed_text:
        suggestions = [
            stop_code for stop_code, stop_description in stop_code_list
            if (
                stop_code.lower().startswith(typed_text.lower())
                or stop_description.lower().startswith(typed_text.lower())
            )
        ]
        suggestion_listbox_start.delete(0, tk.END)
        for suggestion in suggestions:
            suggestion_listbox_start.insert(tk.END, suggestion)
        suggestion_listbox_start.place(x=start_entry.winfo_x(), y=start_entry.winfo_y() + start_entry.winfo_height())
        suggestion_listbox_start.lift()
    else:
        suggestion_listbox_start.delete(0, tk.END)
        suggestion_listbox_start.place_forget()


def select_suggestion_start(event):
    if suggestion_listbox_start.curselection():
        selected_index = suggestion_listbox_start.curselection()[0]
        selected_suggestion = suggestion_listbox_start.get(selected_index)
        start_entry.delete(0, tk.END)
        start_entry.insert(tk.END, selected_suggestion)
        suggestion_listbox_start.delete(0, tk.END)
        suggestion_listbox_start.place_forget()


def update_suggestions_end(event):
    typed_text = event.widget.get()
    if typed_text:
        suggestions = [
            stop_code for stop_code, stop_description in stop_code_list
            if (
                stop_code.lower().startswith(typed_text.lower())
                or stop_description.lower().startswith(typed_text.lower())
            )
        ]
        suggestion_listbox_end.delete(0, tk.END)
        for suggestion in suggestions:
            suggestion_listbox_end.insert(tk.END, suggestion)
        suggestion_listbox_end.place(x=end_entry.winfo_x(), y=end_entry.winfo_y() + end_entry.winfo_height())
        suggestion_listbox_end.lift()
    else:
        suggestion_listbox_end.delete(0, tk.END)
        suggestion_listbox_end.place_forget()


def select_suggestion_end(event):
    if suggestion_listbox_end.curselection():
        selected_index = suggestion_listbox_end.curselection()[0]
        selected_suggestion = suggestion_listbox_end.get(selected_index)
        end_entry.delete(0, tk.END)
        end_entry.insert(tk.END, selected_suggestion)
        suggestion_listbox_end.delete(0, tk.END)
        suggestion_listbox_end.place_forget()


# Create the main window
window = tk.Tk()
window.title("Dijkstra Bus Route")
window.geometry("500x400")

# Create the labels and entries
start_label = tk.Label(window, text="Start:")
start_label.pack()

with open("stops.json", "r") as f:
    stops_data = json.load(f)
stop_code_map = {stop["BusStopCode"]: stop for stop in stops_data}
stop_code_list = [(stop["BusStopCode"], stop["Description"]) for stop in stops_data]

start_entry = tk.Entry(window)
start_entry.pack()
start_entry.bind('<KeyRelease>', update_suggestions_start)

suggestion_listbox_start = tk.Listbox(window, width=30)
suggestion_listbox_start.bind('<<ListboxSelect>>', select_suggestion_start)

end_label = tk.Label(window, text="End:")
end_label.pack()

end_entry = tk.Entry(window)
end_entry.pack()
end_entry.bind('<KeyRelease>', update_suggestions_end)

suggestion_listbox_end = tk.Listbox(window, width=30)
suggestion_listbox_end.bind('<<ListboxSelect>>', select_suggestion_end)

run_button = tk.Button(window, text="Run", command=lambda: run_script_and_enable_button(start_entry, end_entry, result_textbox, view_route_button))
run_button.pack()

result_label = tk.Label(window, text="Results:")
result_label.pack()

result_textbox = ScrolledText(window, width=50, height=10)
result_textbox.pack()

view_route_button = tk.Button(window, text="View Route", command=display_html_file)
view_route_button.pack()
view_route_button.configure(state=tk.DISABLED)

# Run the main window loop
window.mainloop()
