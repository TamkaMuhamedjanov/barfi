import streamlit as st
import pickle
from barfi import save_schema, barfi_schemas, Block, st_barfi
from barfi.manage_schema import delete_schema, load_schema_name
from typing import Dict
import streamlit.components.v1 as components
import json
import time
import ast

def load_schemas(barfi_file_name) -> Dict:
    try:
        with open(f'./data_to_merge/{barfi_file_name}', 'rb') as handle_read:
            schemas = pickle.load(handle_read)
    except FileNotFoundError:
        schemas = {}

    return schemas

def create_scheme(name, schema_data):
  existing_schemes = barfi_schemas()
  try:
    schema_data = ast.literal_eval(schema_data)
    if not type(schema_data) == dict:
      schema_data = ""
    if name in existing_schemes:
      st.toast("Схема с указанным названием существует", icon='⚠️')
      time.sleep(1)
      return
  except:
    schema_data = ""
  save_schema(name, schema_data)
  st.balloons()

def save_scheme(barfi_schema):
  print(barfi_schema)

def delete_scheme(name):
  st.balloons()
  delete_schema(name)

def merge_files(result_file_name, schemes_array):
  schemas = {}
  for item in schemes_array:
    with open(f'{result_file_name}', 'wb') as handle_write:
      schemas[item.get('scheme_name')] = item.get('scheme_data')
      pickle.dump(schemas, handle_write, protocol=pickle.HIGHEST_PROTOCOL)
      handle_write.close()
  st.balloons()

def make_base_blocks():
  feed = Block(name='Feed')
  feed.add_output()
  def feed_func(self):
    self.set_interface(name='Выход 1', value=4)
  feed.add_compute(feed_func)

  splitter = Block(name='Splitter')
  splitter.add_input()
  splitter.add_output()
  splitter.add_output()
  def splitter_func(self):
    in_1 = self.get_interface(name='Вход 1')
    value = in_1 / 2
    self.set_interface(name='Выход 1', value=value)
    self.set_interface(name='Выход 2', value=value)
  splitter.add_compute(splitter_func)

  mixer = Block(name='Mixer')
  mixer.add_input()
  mixer.add_input()
  mixer.add_output()
  def mixer_func(self):
    in_1 = self.get_interface(name='Вход 1')
    in_2 = self.get_interface(name='Вход 2')
    value = in_1 + in_2
    self.set_interface(name='Выход 1', value=value)
  mixer.add_compute(mixer_func)

  result = Block(name='Result')
  result.add_input()
  def result_func(self):
    in_1 = self.get_interface(name='Вход 1')
  result.add_compute(result_func)
  return [feed, splitter, mixer, result]


def main(): 
  st.title("Редактор Barfi-схем") 
  menu = st.sidebar.radio("Меню", [ 
    "Создание схемы",  
    "Список схем",  
    "Просмотр схемы",
    "Удаление схемы", 
    "Слияние схем" 
  ]) 

  if menu == "Создание схемы": 
    st.header("Создание схемы")
    name = st.text_input("Название схемы") 
    schema_data = st.text_area("Данные схемы") 
    st.button("Сохранить", on_click=create_scheme, args=(name, schema_data, ))
    st.subheader("Пример данных схемы")
    st.code(
      '''
      {
      'nodes': [
        {
          'type': 'Feed', 
          'id': 'node_17341976050490', 
          'name': 'Feed-1', 
          'options': [], 
          'state': {}, 
          'interfaces': [[
            'Output 1', 
            {
              'id': 'ni_17341976050491', 
              'value': None
            }
          ]], 
          'position': {
            'x': 41.089179548156956, 
            'y': 233.22473246135553
          }, 
            'width': 200, 
            'twoColumn': False, 
            'customClasses': ''
          }, 
          {
            'type': 'Result', 
            'id': 'node_17341976077762', 
            'name': 'Result-1', 
            'options': [], 
            'state': {}, 
            'interfaces': [[
              'Input 1', 
              {
                'id': 'ni_17341976077773', 
                'value': None
              }
            ]], 
            'position': {
              'x': 385.67895362663495, 
              'y': 233.22473246135553
            }, 
            'width': 200, 
            'twoColumn': False, 
            'customClasses': ''
          }], 
          'connections': [
            {
              'id': '17341976120417', 
              'from': 'ni_17341976050491', 
              'to': 'ni_17341976077773'
            }
          ], 
          'panning': {
            'x': 8.137931034482762, 
            'y': 4.349583828775266
          }, 
          'scaling': 0.9344444444444444
        }''', 'javascript')

  elif menu == "Удаление схемы": 
    st.header("Удаление схемы") 
    if len(barfi_schemas()) == 0:
      st.toast("Схемы не найдены", icon='⚠️')
    else:
      option = st.selectbox(
      "Выберите схему",
      tuple(barfi_schemas()),
      index=None,
      )
      if option:
        st.button("Удалить", on_click=delete_scheme, args=(option,))
  
  elif menu == "Список схем":
    st.header("Список схем") 
    for item in barfi_schemas():
      components.html(
        f"<details style='color: #fff'><summary>{item}</summary><p>{json.dumps(load_schema_name(item))}</p></details>"
      )
  
  elif menu == "Просмотр схемы":
    load_schema = st.selectbox('Выберите схему для просмотра:', barfi_schemas())
    barfi_result = st_barfi(base_blocks=make_base_blocks(), load_schema=load_schema, compute_engine=False)

    if barfi_result:
      st.write(barfi_result)

  elif menu == "Слияние схем": 
    st.header("Слияние схем") 
    uploaded_files = st.file_uploader( 
      "Выберите .barfi файлы",  
      type=['barfi'],  
      accept_multiple_files=True 
    )
    if uploaded_files:
      total_schemes = []
      for item in uploaded_files:
          bar_dic = load_schemas(item.name)
          for key in bar_dic.keys():
            total_schemes.append({"scheme_name": key, "scheme_data": bar_dic.get(key)})
      st.button("Объединить", on_click=merge_files, args=('schemas.barfi', total_schemes)) 

main()