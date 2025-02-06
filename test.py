import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
from faker import Faker
import random
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import plotly.express as px

fake = Faker('zh_CN')
# Create the Streamlit app with a sidebar for navigation
st.set_page_config(page_title="皮肤病患者管理系统", layout="wide")
st.title("皮肤病患者管理系统")
st.image("hzban.png")
# Sidebar for navigation
st.sidebar.title("菜单导航")
app_mode = st.sidebar.selectbox("请选择", ["添加患者", "导入患者数据", "患者及用药情况","患者信息查询"])

# import os
# # 设置环境变量以确保正确加载资源
# os.environ['STREAMLIT_AGGRID_URL'] = './st_aggrid/frontend/build'
# # 设置环境变量，强制使用本地资源
# os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
# # 设置基础路径
# os.environ["STREAMLIT_STATIC_PATH"] = os.path.join(os.path.dirname(__file__), "streamlit/static")
# os.environ["STREAMLIT_COMPONENTS_PATH"] = os.path.join(os.path.dirname(__file__), "st_aggrid/frontend/build")


@st.cache_resource
def create_database():
    conn = sqlite3.connect('patients.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT ,
            birth_date DATE ,
            age INTEGER ,
            contact TEXT ,
            address TEXT ,
            height REAL ,
            weight REAL ,
            insurance_type TEXT ,
            care_status TEXT ,
            monthly_income TEXT ,
            cooperation TEXT ,
            is_chronic_disease TEXT ,
            skin_disease_name TEXT ,
            skin_disease_history TEXT ,
            elderly_itch_related_disease TEXT,
            chronic_disease TEXT ,
            care_provider TEXT DEFAULT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            antibiotic_name TEXT,
            painkiller_name TEXT,
            anticancer_name TEXT,
            antidepressant_name TEXT,
            skin_disease_medication TEXT,
            medication_date DATE,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    conn.commit()
    conn.close()

create_database()

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('patients.db')
    return conn

# Function to generate test data
def generate_test_data(num_records=10):
    test_data = []
    for _ in range(num_records):
        name = fake.name()
        gender = random.choice(["男", "女"])
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
        age = (datetime.now().date() - birth_date).days // 365
        contact = fake.phone_number()
        address = fake.address()
        height = random.uniform(150, 200)
        weight = random.uniform(40, 150)
        insurance_type = random.choice(["城镇居民医疗保险", "公费医疗", "新农合", "商业保险", "军队优惠医疗", "自费", "其他"])
        care_status = random.choice(["与老伴同住", "与子女同住", "与保姆同住", "独居", "养老院", "其他"])
        monthly_income = random.choice(["≤3000", "3000-5000", "5000-10000", "≥10000"])
        cooperation = random.choice(["是", "否"])
        is_chronic_disease = random.choice(["白癜风", "斑秃", "类风湿", "系统性红斑狼疮", "炎症性肠病", "幽门螺旋菌感染"])
        skin_disease_name = fake.word()
        skin_disease_history = fake.sentence()
        elderly_itch_related_disease = random.choice(["支气管哮喘", "糖尿病", "肝病", "肾功能不全", "其他"])
        chronic_disease = random.sample(["高血压", "冠心病", "脑卒中", "焦虑症", "抑郁症", "老年阿尔茨海默症", "帕金森", "哮喘", "其他"], random.randint(1, 3))
        care_provider = fake.name()
        test_data.append((name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, is_chronic_disease,skin_disease_name, skin_disease_history, elderly_itch_related_disease, ','.join(chronic_disease),care_provider))
    return test_data

# Function to import test data
# def import_test_data():
#     test_data = generate_test_data()
#     conn = get_db_connection()
#     conn.executemany('''INSERT INTO patients (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, is_chronic_disease,skin_disease_name, skin_disease_history, elderly_itch_related_disease, chronic_disease) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', test_data)
#     conn.commit()
#     conn.close()
#     st.success("测试数据导入成功！")

def import_combined_data():
    st.subheader("导入患者及用药数据")
    uploaded_file = st.file_uploader("选择一个CSV或Excel文件", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file, skiprows=1)
        else:
            data = pd.read_excel(uploaded_file, skiprows=1)

        # Ensure the required columns are present
        required_patient_columns = ["name", "gender", "birth_date", "age", "contact", "address", "height", "weight", "insurance_type", "care_status", "monthly_income", "cooperation", "is_chronic_disease","skin_disease_name", "skin_disease_history", "elderly_itch_related_disease", "chronic_disease","care_provider"]
        required_medication_columns = ["patient_id", "antibiotic_name", "painkiller_name", "anticancer_name", "antidepressant_name", "skin_disease_medication", "medication_date"]

        # if not all(column in data.columns for column in required_patient_columns):
        #     st.error("CSV/Excel文件缺少患者信息列，请检查文件格式。")
        #     return

        # if not all(column in data.columns for column in required_medication_columns):
        #     st.error("CSV/Excel文件缺少用药信息列，请检查文件格式。")
        #     return

        # Insert patient data
        patient_data = data[required_patient_columns]
        conn = get_db_connection()
        patient_data.to_sql('patients', conn, if_exists='append', index=False)
        conn.commit()

        # Get the last inserted patient IDs
        # last_patient_id = conn.execute("SELECT id FROM patients ORDER BY id DESC LIMIT 1").fetchone()[0]
        # patient_count = len(patient_data)

        # Adjust patient IDs in medication data
        medication_data = data[required_medication_columns]
        # medication_data['patient_id'] = range(last_patient_id - patient_count + 1, last_patient_id + 1)

        # Insert medication data
        medication_data.to_sql('medications', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()

        st.success("患者及用药数据导入成功！")


# Uncomment the following line to import test data
# import_test_data()



# Function to add patient information
def add_patient():
    st.subheader("添加患者信息")
    with st.form(key='add_patient_form'):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名")
            gender = st.selectbox("性别", ["男", "女"], index=0)
            birth_date = st.date_input("出生日期")
            age = (datetime.now().date() - birth_date).days // 365  # Calculate age
            contact = st.text_input("联系方式", max_chars=11)  # Limit to 11 characters
            address = st.text_area("地址")
            skin_disease_name = st.text_input("皮肤病名称")
            is_chronic_disease = st.selectbox("患自身免疫性疾病", ["白癜风", "斑秃", "类风湿", "系统性红斑狼疮", "炎症性肠病", "幽门螺旋菌感染",""])  
            elderly_itch_related_disease = st.selectbox("老年瘙痒症相关疾病", ["支气管哮喘", "糖尿病", "肝病", "肾功能不全", "其他",""])
            care_provider = st.text_input("保健人员名")
        with col2:
            height = st.number_input("身高 (cm)", min_value=0.0)
            weight = st.number_input("体重 (kg)", min_value=0.0)
            insurance_type = st.selectbox("医保类型", ["城镇居民医疗保险", "公费医疗", "新农合", "商业保险", "军队优惠医疗", "自费", "其他",""])
            care_status = st.selectbox("照顾状况", ["与老伴同住", "与子女同住", "与保姆同住", "独居", "养老院", "其他",""])
            monthly_income = st.selectbox("个人月收入", ["≤3000", "3000-5000", "5000-10000", "≥10000",""])
            cooperation = st.selectbox("能否正常配合调查", ["是", "否",""])            
            skin_disease_history = st.text_area("皮肤病史")            
            chronic_disease = st.multiselect("慢性病", ["高血压", "冠心病", "脑卒中", "焦虑症", "抑郁症", "老年阿尔茨海默症", "帕金森", "哮喘", "其他",""])

        submit_button = st.form_submit_button("添加患者")
        if submit_button:
            conn = get_db_connection()
            conn.execute('''INSERT INTO patients (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, is_chronic_disease,skin_disease_name, skin_disease_history, elderly_itch_related_disease, chronic_disease,care_provider) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, is_chronic_disease,skin_disease_name, skin_disease_history, elderly_itch_related_disease, ','.join(chronic_disease),care_provider))
            conn.commit()
            conn.close()
            st.success("患者信息添加成功！")

# Function to import patient data from CSV or Excel
# def import_patient_data():
#     st.subheader("导入患者数据")
#     uploaded_file = st.file_uploader("选择一个CSV或Excel文件", type=["csv", "xlsx"])
#     if uploaded_file is not None:
#         if uploaded_file.name.endswith('.csv'):
#             data = pd.read_csv(uploaded_file)
#         else:
#             data = pd.read_excel(uploaded_file)

#         for index, row in data.iterrows():
#             conn = get_db_connection()
#             conn.execute('''INSERT INTO patients (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, skin_disease_name, skin_disease_history, elderly_itch_related_disease, chronic_disease) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
#                          (row['name'], row['gender'], row['birth_date'], row['age'], row['contact'], row['address'], row['height'], row['weight'], row['insurance_type'], row['care_status'], row['monthly_income'], row['cooperation'], row['skin_disease_name'], row['skin_disease_history'], row['elderly_itch_related_disease'], row['chronic_disease']))
#             conn.commit()
#             conn.close()
#         st.success("患者数据导入成功！")

# Function to edit patient information
def edit_patient():
    if 'edit_patient_id' in st.session_state and st.session_state.display_patient:
    # if st.session_state.edit_patient_id  and st.session_state.display_patient:    
        patient_id = st.session_state.edit_patient_id
        patient_data = st.session_state.edit_patient_data
        # Debugging: Print patient_data to check its format
        # st.write("Patient Data:", patient_data)

        st.subheader("编辑患者信息")
        with st.form(key='edit_patient_form'):
            # st.write("XXX：", patient_id)
            name = st.text_input("姓名", value=patient_data['name'].item())
            gender = st.selectbox("性别", ["男", "女"], index=0 if patient_data['gender'].item() == "男" else 1)
            birth_date = st.date_input("出生日期", value=pd.to_datetime(patient_data['birth_date'].item()))
            age = st.number_input("年龄", min_value=0, value=patient_data['age'].item())
            contact = st.text_input("联系方式", value=patient_data['contact'].item())
            address = st.text_area("地址", value=patient_data['address'].item())
            height = st.number_input("身高 (cm)", min_value=0, value=int(patient_data['height'].item()))
            weight = st.number_input("体重 (kg)", min_value=0, value=int(patient_data['weight'].item()))
            insurance_type = st.selectbox("医保类型", ["城镇居民医疗保险", "公费医疗", "新农合", "商业保险", "军队优惠医疗", "自费", "其他",""], index=["城镇居民医疗保险", "公费医疗", "新农合", "商业保险", "军队优惠医疗", "自费", "其他",""].index(patient_data['insurance_type'].item()))
            care_status = st.selectbox("照顾状况", ["与老伴同住", "与子女同住", "与保姆同住", "独居", "养老院", "其他",""], index=["与老伴同住", "与子女同住", "与保姆同住", "独居", "养老院", "其他",""].index(patient_data['care_status'].item()))
            monthly_income = st.selectbox("个人月收入", ["≤3000", "3000-5000", "5000-10000", "≥10000",""], index=["≤3000", "3000-5000", "5000-10000", "≥10000",""].index(patient_data['monthly_income'].item()))
            cooperation = st.selectbox("能否正常配合调查", ["是", "否"], index=0 if patient_data['cooperation'].item() == "是" else 1)
            is_chronic_disease = st.selectbox("患自身免疫性疾病",["白癜风", "斑秃", "类风湿", "系统性红斑狼疮", "炎症性肠病", "幽门螺旋菌感染",""], index=["白癜风", "斑秃", "类风湿", "系统性红斑狼疮", "炎症性肠病", "幽门螺旋菌感染",""].index(patient_data['is_chronic_disease'].item()))
            # is_chronic_disease = st.selectbox("是否患有自身免疫性疾病", ["白癜风", "斑秃", "类风湿", "系统性红斑狼疮", "炎症性肠病", "幽门螺旋菌感染"])
            skin_disease_name = st.text_input("皮肤病名称", value=patient_data['skin_disease_name'].item())
            skin_disease_history = st.text_area("皮肤病史", value=patient_data['skin_disease_history'].item())
            elderly_itch_related_disease = st.text_input("老年瘙痒症相关疾病", value=patient_data['elderly_itch_related_disease'].item())
            chronic_disease = st.multiselect("慢性病", ["高血压", "冠心病", "脑卒中", "焦虑症", "抑郁症", "老年阿尔茨海默症", "帕金森", "哮喘", "其他",""], default=patient_data['chronic_disease'].item().split(','))
            care_provider = st.text_input("保健人员名", value=patient_data['care_provider'].item()) 
            submit_button = st.form_submit_button("更新患者")
            if submit_button:
                conn = get_db_connection()
                conn.execute('''UPDATE patients SET name=?, gender=?, birth_date=?, age=?, contact=?, address=?, height=?, weight=?, insurance_type=?, care_status=?, monthly_income=?, cooperation=?,is_chronic_disease =?, skin_disease_name=?, skin_disease_history=?, elderly_itch_related_disease=?, chronic_disease=? ,care_provider=? WHERE id=?''',
                             (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation,is_chronic_disease, skin_disease_name, skin_disease_history, elderly_itch_related_disease, ','.join(chronic_disease),care_provider, patient_id))
                conn.commit()
                conn.close()
                st.success("患者信息更新成功！")
                del st.session_state.edit_patient_id
                del st.session_state.edit_patient_data
                time.sleep(2)
                st.session_state.display_patient = False
                st.rerun()
      
                # st.experimental_user
        

def display_patients():
        # Initialize session state
    if 'show_medications' not in st.session_state:
        st.session_state.show_medications = False
    if 'selected_patient_id' not in st.session_state:
        st.session_state.selected_patient_id = None
    if 'display_patient' not in st.session_state:    
        st.session_state.display_patient = False
    if 'edit_medication_id' not in st.session_state:
        st.session_state.edit_medication_id = None
    if 'edit_medication_data' not in st.session_state:
        st.session_state.edit_medication_data = None
    patients_container = st.container()
    medications_container = st.container()
    add_medication_container = st.container()  
    with patients_container:
        st.subheader("患者信息")
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM patients", conn)
        conn.close()

        # Search functionality
        search_term = st.text_input("按姓名或联系方式搜索")
        if search_term:
            df = df[df['name'].str.contains(search_term, case=False, na=False) | df['contact'].str.contains(search_term, case=False, na=False)]

        # Pagination
        page_size = st.number_input("每页记录数", min_value=1, value=10)
        page_number = st.number_input("页码", min_value=1, value=1)
        total_pages = (len(df) + page_size - 1) // page_size

        if page_number > total_pages:
            page_number = total_pages

        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        df_page = df[start_index:end_index]

        # AgGrid configuration
        gb = GridOptionsBuilder.from_dataframe(df_page)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=page_size)  # Add pagination
        gb.configure_side_bar()  # Add a sidebar
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
        gb.configure_selection(selection_mode="multiple", use_checkbox=True, groupSelectsChildren="Group checkbox select children")  # Enable multi-row selection
        gb.configure_grid_options(ensureDomOrder=True, allowUnsafeJsCode=True)

        # Set column headers to Chinese
        gb.configure_column("name", header_name="姓名")
        gb.configure_column("gender", header_name="性别")
        gb.configure_column("birth_date", header_name="出生日期")
        gb.configure_column("age", header_name="年龄")
        gb.configure_column("contact", header_name="联系方式")
        gb.configure_column("address", header_name="地址")
        gb.configure_column("height", header_name="身高 (cm)")
        gb.configure_column("weight", header_name="体重 (kg)")
        gb.configure_column("insurance_type", header_name="医保类型")
        gb.configure_column("care_status", header_name="照顾状况")
        gb.configure_column("monthly_income", header_name="个人月收入")
        gb.configure_column("cooperation", header_name="能否正常配合调查")
        gb.configure_column("is_chronic_disease", header_name="患自身免疫性疾病")
        gb.configure_column("skin_disease_name", header_name="皮肤病名称")
        gb.configure_column("skin_disease_history", header_name="皮肤病史")
        gb.configure_column("elderly_itch_related_disease", header_name="老年瘙痒症相关疾病")
        gb.configure_column("chronic_disease", header_name="慢性病")
        gb.configure_column("care_provider", header_name="保健人员名") 

        gridOptions = gb.build()
        @st.cache_resource
        def load_aggrid():
            return AgGrid
        
        
        response = load_aggrid()(
            df_page,
            gridOptions=gridOptions,
            enable_enterprise_modules=True,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode="FILTERED",  # Use 'FILTERED' to get the filtered data
            fit_columns_on_grid_load=False,
            allow_unsafe_jscode=True,
            excel_export_mode="MANUAL"
        )

        # Handle row selection
        # selected_rows = pd.DataFrame(response['selected_rows'])  # Use 'selected_rows' to get the selected rows
        # # Debugging: Print selected_rows to check its format
        # st.write("Selected Rows:",type(selected_rows))


        if response['selected_rows'] is not None:
            # Ensure each row is a dictionary
            row = pd.DataFrame(data=response['selected_rows'],index=None)
            # if isinstance(selected_rows, list) and all(isinstance(row, dict) for row in selected_rows):
            selected_ids =  row['id']
            # st.write("Selected Rows:",selected_ids)

            # Edit and delete functionality
            if row is not None and len(row) == 1:
                # st.write("Selected Row:",row)
                patient_id = row['id'].item()
                # st.write("Sucessfully")
                col1, col2, col3 = st.columns(3)
                with col1:
                    edit_button = st.button("编辑患者信息", key="edit_patient")
                with col2:
                    delete_button = st.button("删除患者信息", key="delete_patient")
                with col3:
                    view_medications_button = st.button("查看用药信息", key="view_med")
                
                if edit_button:
                    st.session_state.edit_patient_id = patient_id
                    st.session_state.edit_patient_data = row
                    st.session_state.display_patient = True

                if delete_button:
                    conn = get_db_connection()
                    conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                    # 删除该患者的用药信息
                    conn.execute("DELETE FROM medications WHERE patient_id = ?", (patient_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"删除患者 {row['name'].item()} 成功！")
                    time.sleep(2)
                    st.rerun()                 

                if view_medications_button:
                    # display_medications(patient_id)
                    # add_medication(patient_id)
                    st.session_state.show_medications = True
                    st.session_state.selected_patient_id = patient_id

            # else:
            #     st.write("选中的行数据格式不正确。")
        else:
            st.write("请选择一行进行操作。")
            time.sleep(3)
            st.session_state.show_medications = False
            st.session_state.display_patient = False
            st.session_state.show_edit_medication = False
            
        # Display medications if requested
    if st.session_state.show_medications and st.session_state.selected_patient_id:
        display_medications(st.session_state.selected_patient_id, medications_container)
        add_medication(st.session_state.selected_patient_id, add_medication_container)     

       
# Function to display medication information for a selected patient
def display_medications(patient_id,medications_container):
            # Initialize session state
    if 'show_edit_medication' not in st.session_state:    
        st.session_state.show_edit_medication = False

    with medications_container:
        st.subheader("用药信息")
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM medications WHERE patient_id = ?", conn, params=(patient_id,))
        conn.close()

        if df.empty:
            st.write("未找到该患者的用药记录。")
        else:
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)  # Add pagination
            gb.configure_side_bar()  # Add a sidebar
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
            gb.configure_selection(selection_mode="multiple", use_checkbox=True, groupSelectsChildren="Group checkbox select children")  # Enable multi-row selection
            gb.configure_grid_options(ensureDomOrder=True, allowUnsafeJsCode=True)
            
            # Set column headers to Chinese
            gb.configure_column("antibiotic_name", header_name="抗生素名称")
            gb.configure_column("painkiller_name", header_name="止痛药名称")
            gb.configure_column("anticancer_name", header_name="抗癌药名称")
            gb.configure_column("antidepressant_name", header_name="抗抑郁药名称")
            gb.configure_column("skin_disease_medication", header_name="皮肤病用药名称")
            gb.configure_column("medication_date", header_name="用药日期")
            
            gridOptions = gb.build()
            @st.cache_resource
            def load_aggrid():
                return AgGrid
            response1 = load_aggrid()(
                df,
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                data_return_mode="AS_INPUT",
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True
            )

            # Handle row selection
            row1 = pd.DataFrame(response1['selected_rows'],index=None)
            # selected_ids = row['id']

            # Edit and delete functionality
            if row1 is not None and len(row1) == 1 :            
                medication_id = row1['id'].item()
                col1, col2 = st.columns(2)
                with col1:
                    edit_button1 = st.button("编辑用药记录", key="edit_med")
                with col2:    
                    delete_button1 = st.button("删除用药记录", key="delete_med")

                if edit_button1:
                    st.session_state.edit_medication_id = medication_id                    
                    st.session_state.edit_medication_data = row1
                    st.session_state.show_edit_medication = True
                    

                if delete_button1:
                    conn = get_db_connection()
                    conn.execute("DELETE FROM medications WHERE id = ?", (medication_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"删除用药记录{row1['id']} 成功！")
                    time.sleep(2)
                    st.rerun()
    if st.session_state.show_edit_medication and st.session_state.edit_medication_id:
        edit_medication()
              
def edit_medication():
    
    if 'edit_medication_id' in st.session_state and 'edit_medication_data' in st.session_state and st.session_state.show_edit_medication:
        medication_id = st.session_state.edit_medication_id
        medication_data = st.session_state.edit_medication_data
        # st.write("id",medication_id)
        # st.write("edit_medication_data",medication_data)
        st.subheader("编辑用药信息")
        with st.form(key='edit_medication_form'):
            antibiotic_name = st.text_input("抗生素名称", value=medication_data['antibiotic_name'].item())
            painkiller_name = st.text_input("止痛药名称", value=medication_data['painkiller_name'].item())
            anticancer_name = st.text_input("抗癌药名称", value=medication_data['anticancer_name'].item())
            antidepressant_name = st.text_input("抗抑郁药名称", value=medication_data['antidepressant_name'].item())
            skin_disease_medication = st.text_input("皮肤病用药名称", value=medication_data['skin_disease_medication'].item())
            medication_date = st.date_input("用药日期", value=pd.to_datetime(medication_data['medication_date'].item()))

            submit_button = st.form_submit_button("更新用药")
            if submit_button:
                conn = get_db_connection()
                conn.execute('''UPDATE medications SET antibiotic_name=?, painkiller_name=?, anticancer_name=?, antidepressant_name=?, skin_disease_medication=?, medication_date=? WHERE id=?''',
                             (antibiotic_name, painkiller_name, anticancer_name, antidepressant_name, skin_disease_medication, medication_date, medication_id))
                conn.commit()
                conn.close()
                st.success("用药信息更新成功！")
                # del st.session_state.edit_medication_id
                # del st.session_state.edit_medication_data
                time.sleep(3)
                st.session_state.show_edit_medication = False
                st.rerun()
    # st.rerun()
      
# Function to add medication information for a selected patient
def add_medication(patient_id,add_medication_container):
    with add_medication_container:
        st.subheader("添加用药信息")
        with st.form(key='add_medication_form'):
            antibiotic_name = st.text_input("抗生素名称")
            painkiller_name = st.text_input("止痛药名称")
            anticancer_name = st.text_input("抗癌药名称")
            antidepressant_name = st.text_input("抗抑郁药名称")
            skin_disease_medication = st.text_input("皮肤病用药名称")
            medication_date = st.date_input("用药日期")

            submit_button = st.form_submit_button("添加用药")
            if submit_button:
                conn = get_db_connection()
                conn.execute('''INSERT INTO medications (patient_id, antibiotic_name, painkiller_name, anticancer_name, antidepressant_name, skin_disease_medication, medication_date) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (patient_id, antibiotic_name, painkiller_name, anticancer_name, antidepressant_name, skin_disease_medication, medication_date))
                conn.commit()
                conn.close()
                st.success("用药信息添加成功！")
                
def query_patient_medication():
    st.subheader("患者及用药信息查询")
    conn = get_db_connection()
    query = """
    SELECT 
        p.id AS 患者ID,
        p.name AS 姓名,
        p.gender AS 性别,
        p.birth_date AS 出生日期,
        p.age AS 年龄,
        p.contact AS 联系方式,
        p.address AS 地址,
        p.height AS 身高,
        p.weight AS 体重,
        p.insurance_type AS 医保类型,
        p.care_status AS 照顾状况,
        p.monthly_income AS 个人月收入,
        p.cooperation AS 能否正常配合调查,
        p.is_chronic_disease as 患自身免疫性疾病,
        p.skin_disease_name AS 皮肤病名称,
        p.skin_disease_history AS 皮肤病史,
        p.elderly_itch_related_disease AS 老年瘙痒症相关疾病,
        p.chronic_disease AS 慢性病,
        p.care_provider AS 保健人员名,
        m.id AS 用药记录ID,
        m.antibiotic_name AS 抗生素名称,
        m.painkiller_name AS 止痛药名称,
        m.anticancer_name AS 抗癌药名称,
        m.antidepressant_name AS 抗抑郁药名称,
        m.skin_disease_medication AS 皮肤病用药名称,
        m.medication_date AS 用药日期
    FROM patients p
    left JOIN medications m ON p.id = m.patient_id
    """
    df = pd.read_sql_query(query, conn)
    df1 = pd.read_sql_query("SELECT monthly_income FROM patients", conn)
    conn.close()

    # Search functionality
    search_term = st.text_input("按姓名或联系方式搜索")
    if search_term:
        df = df[df['姓名'].str.contains(search_term, case=False, na=False) | df['联系方式'].str.contains(search_term, case=False, na=False)]

    # Pagination
    page_size = st.number_input("每页记录数", min_value=1, value=10)
    page_number = st.number_input("页码", min_value=1, value=1)
    total_pages = (len(df) + page_size - 1) // page_size

    if page_number > total_pages:
        page_number = total_pages

    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    df_page = df[start_index:end_index]

    # AgGrid configuration
    gb = GridOptionsBuilder.from_dataframe(df_page)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=page_size)  # Add pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True, groupSelectsChildren="Group checkbox select children")  # Enable multi-row selection
    gb.configure_grid_options(ensureDomOrder=True, allowUnsafeJsCode=True)

    gridOptions = gb.build()

    AgGrid(
        df_page,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode="FILTERED",  # Use 'FILTERED' to get the filtered data
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        excel_export_mode="MANUAL"
    )

    st.subheader("📊图表统计展示📈")
    col1, col2 = st.columns(2)
     # 按组别每月数量
    cot_med_type = df.groupby(["医保类型"]).size().reset_index(name="数量")
    bar_graph = px.bar(
        cot_med_type,
        x="医保类型",
        y="数量",
        title="按医保类型统计",
        color="医保类型",
        # facet_col="remarks"
    )
    # 设置 x 轴和 y 轴标签
    bar_graph.update_xaxes(title_text="医保类型")
    bar_graph.update_yaxes(title_text="医保类型数量")
    col1.plotly_chart(bar_graph)

    #月收入
    income_counts = df['个人月收入'].value_counts().reset_index(name='数量')
    income_counts.columns = ['个人月收入', '数量']

    # Create a pie chart using Plotly
    fig = px.pie(income_counts, names='个人月收入', values='数量', title='按月收入统计患者数量')

    # Display the pie chart in Streamlit
    col2.plotly_chart(fig)
    
    col3, col4 = st.columns(2)

    # 将慢性病从逗号分隔的字符串转换为单独的行
    # df_chronic = df['慢性病'].str.split(',', expand=True).stack().reset_index(level=1, drop=True)
    # df_chronic = df_chronic.reset_index()
    # df_chronic.columns = ['患者ID', '慢性病']
    

    # # 合并数据
    # df_merged = pd.merge(df, df_chronic, on='患者ID')
    # st.write(df.head())
    # st.write(df_merged)
    # 按皮肤病、老年瘙痒症相关疾病和慢性病统计患者数量
    df_grouped = df.groupby(['皮肤病名称', '老年瘙痒症相关疾病', '慢性病']).size().reset_index(name='患者数量')
    # st.write(df_grouped)
    # 绘制堆叠条形图
    fig = px.bar(df_grouped, x='皮肤病名称', y='患者数量', color='慢性病', barmode='stack',
                 title='皮肤病、老年瘙痒症相关疾病与慢性病与患者数量关系',
                 labels={'皮肤病名称': '皮肤病', '老年瘙痒症相关疾病': '老年瘙痒症相关疾病', '慢性病': '慢性病', '患者数量': '患者数量'})

    # 设置 x 轴和 y 轴标签
    fig.update_xaxes(title_text="皮肤病")
    fig.update_yaxes(title_text="患者数量")

    col3.plotly_chart(fig)

    # 可以添加其他图表，例如按老年瘙痒症相关疾病分组的患者数量
    df_grouped_itch = df.groupby(['老年瘙痒症相关疾病', '慢性病']).size().reset_index(name='患者数量')

    fig_itch = px.bar(df_grouped_itch, x='老年瘙痒症相关疾病', y='患者数量', color='慢性病', barmode='stack',
                      title='老年瘙痒症相关疾病与慢性病与患者数量关系',
                      labels={'老年瘙痒症相关疾病': '老年瘙痒症相关疾病', '慢性病': '慢性病', '患者数量': '患者数量'})

    # 设置 x 轴和 y 轴标签
    fig_itch.update_xaxes(title_text="老年瘙痒症相关疾病")
    fig_itch.update_yaxes(title_text="患者数量")

    col4.plotly_chart(fig_itch)


# Call the functions based on the selected app mode
if app_mode == "添加患者":
    add_patient()
elif app_mode == "导入患者数据":
    import_combined_data()
elif app_mode == "患者及用药情况":
    display_patients()
    edit_patient()
    # edit_medication()
elif app_mode == "患者信息查询":
    query_patient_medication()
    
