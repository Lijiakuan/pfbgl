import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
from faker import Faker
import random
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

fake = Faker('zh_CN')
# Create the Streamlit app with a sidebar for navigation
st.set_page_config(page_title="皮肤病患者管理系统", layout="wide")
st.title("皮肤病患者管理系统")

# Sidebar for navigation
st.sidebar.title("菜单导航")
app_mode = st.sidebar.selectbox("请选择", ["添加患者", "导入患者数据", "患者及用药情况","患者信息查询"])
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
            height INTEGER ,
            weight INTEGER ,
            insurance_type TEXT ,
            care_status TEXT ,
            monthly_income TEXT ,
            cooperation TEXT ,
            skin_disease_name TEXT ,
            skin_disease_history TEXT ,
            elderly_itch_related_disease TEXT,
            chronic_disease TEXT 
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
        skin_disease_name = fake.word()
        skin_disease_history = fake.sentence()
        elderly_itch_related_disease = random.choice(["支气管哮喘", "糖尿病", "肝病", "肾功能不全", "其他"])
        chronic_disease = random.sample(["高血压", "冠心病", "脑卒中", "焦虑症", "抑郁症", "老年阿尔茨海默症", "帕金森", "哮喘", "其他"], random.randint(1, 3))
        
        test_data.append((name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, skin_disease_name, skin_disease_history, elderly_itch_related_disease, ','.join(chronic_disease)))
    return test_data

# Function to import test data
def import_test_data():
    test_data = generate_test_data()
    conn = get_db_connection()
    conn.executemany('''INSERT INTO patients (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, skin_disease_name, skin_disease_history, elderly_itch_related_disease, chronic_disease) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', test_data)
    conn.commit()
    conn.close()
    st.success("测试数据导入成功！")

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
            elderly_itch_related_disease = st.selectbox("老年瘙痒症相关疾病", ["支气管哮喘", "糖尿病", "肝病", "肾功能不全", "其他"])
        with col2:
            height = st.number_input("身高 (cm)", min_value=0.0)
            weight = st.number_input("体重 (kg)", min_value=0.0)
            insurance_type = st.selectbox("医保类型", ["城镇居民医疗保险", "公费医疗", "新农合", "商业保险", "军队优惠医疗", "自费", "其他"])
            care_status = st.selectbox("照顾状况", ["与老伴同住", "与子女同住", "与保姆同住", "独居", "养老院", "其他"])
            monthly_income = st.selectbox("个人月收入", ["≤3000", "3000-5000", "5000-10000", "≥10000"])
            cooperation = st.selectbox("能否正常配合调查", ["是", "否"])            
            skin_disease_history = st.text_area("皮肤病史")            
            chronic_disease = st.multiselect("慢性病", ["高血压", "冠心病", "脑卒中", "焦虑症", "抑郁症", "老年阿尔茨海默症", "帕金森", "哮喘", "其他"])

        submit_button = st.form_submit_button("添加患者")
        if submit_button:
            conn = get_db_connection()
            conn.execute('''INSERT INTO patients (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, skin_disease_name, skin_disease_history, elderly_itch_related_disease, chronic_disease) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, skin_disease_name, skin_disease_history, elderly_itch_related_disease, ','.join(chronic_disease)))
            conn.commit()
            conn.close()
            st.success("患者信息添加成功！")

# Function to import patient data from CSV or Excel
def import_patient_data():
    st.subheader("导入患者数据")
    uploaded_file = st.file_uploader("选择一个CSV或Excel文件", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                # 尝试多种编码格式
                try:
                    data = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        uploaded_file.seek(0)  # 重置文件指针
                        data = pd.read_csv(uploaded_file, encoding='gbk')
                    except UnicodeDecodeError:
                        uploaded_file.seek(0)  # 重置文件指针
                        data = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                data = pd.read_excel(uploaded_file)

            for index, row in data.iterrows():
                conn = get_db_connection()
                conn.execute('''INSERT INTO patients (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, skin_disease_name, skin_disease_history, elderly_itch_related_disease, chronic_disease) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (row['name'], row['gender'], row['birth_date'], row['age'], row['contact'], row['address'], row['height'], row['weight'], row['insurance_type'], row['care_status'], row['monthly_income'], row['cooperation'], row['skin_disease_name'], row['skin_disease_history'], row['elderly_itch_related_disease'], row['chronic_disease']))
                conn.commit()
                conn.close()
            st.success("患者数据导入成功！")
        except Exception as e:
            st.error(f"导入数据时出错: {str(e)}")
        
def import_medications_data():
    st.subheader("导入用药数据")
    uploaded_file = st.file_uploader("选择一个CSV或Excel文件", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                # 尝试多种编码格式
                try:
                    data = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        uploaded_file.seek(0)  # 重置文件指针
                        data = pd.read_csv(uploaded_file, encoding='gbk')
                    except UnicodeDecodeError:
                        uploaded_file.seek(0)  # 重置文件指针
                        data = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                data = pd.read_excel(uploaded_file)


            for index, row in data.iterrows():
                conn = get_db_connection()
                conn.execute('''INSERT INTO medications (patient_id, antibiotic_name, painkiller_name, anticancer_name, antidepressant_name, skin_disease_medication, medication_date) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (row['patient_id'], row['antibiotic_name'], row['painkiller_name'], row['anticancer_name'], row['antidepressant_name'], row['skin_disease_medication'], row['medication_date']))
                conn.commit()
                conn.close()
            st.success("患者数据导入成功！")
        except Exception as e:
            st.error(f"导入数据时出错: {str(e)}")

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
            insurance_type = st.selectbox("医保类型", ["城镇居民医疗保险", "公费医疗", "新农合", "商业保险", "军队优惠医疗", "自费", "其他"], index=["城镇居民医疗保险", "公费医疗", "新农合", "商业保险", "军队优惠医疗", "自费", "其他"].index(patient_data['insurance_type'].item()))
            care_status = st.selectbox("照顾状况", ["与老伴同住", "与子女同住", "与保姆同住", "独居", "养老院", "其他"], index=["与老伴同住", "与子女同住", "与保姆同住", "独居", "养老院", "其他"].index(patient_data['care_status'].item()))
            monthly_income = st.selectbox("个人月收入", ["≤3000", "3000-5000", "5000-10000", "≥10000"], index=["≤3000", "3000-5000", "5000-10000", "≥10000"].index(patient_data['monthly_income'].item()))
            cooperation = st.selectbox("能否正常配合调查", ["是", "否"], index=0 if patient_data['cooperation'].item() == "是" else 1)
            skin_disease_name = st.text_input("皮肤病名称", value=patient_data['skin_disease_name'].item())
            skin_disease_history = st.text_area("皮肤病史", value=patient_data['skin_disease_history'].item())
            elderly_itch_related_disease = st.text_input("老年瘙痒症相关疾病", value=patient_data['elderly_itch_related_disease'].item())
            chronic_disease = st.multiselect("慢性病", ["高血压", "冠心病", "脑卒中", "焦虑症", "抑郁症", "老年阿尔茨海默症", "帕金森", "哮喘", "其他"], default=patient_data['chronic_disease'].item().split(','))
            submit_button = st.form_submit_button("更新患者")
            if submit_button:
                conn = get_db_connection()
                conn.execute('''UPDATE patients SET name=?, gender=?, birth_date=?, age=?, contact=?, address=?, height=?, weight=?, insurance_type=?, care_status=?, monthly_income=?, cooperation=?, skin_disease_name=?, skin_disease_history=?, elderly_itch_related_disease=?, chronic_disease=? WHERE id=?''',
                             (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, skin_disease_name, skin_disease_history, elderly_itch_related_disease, ','.join(chronic_disease), patient_id))
                conn.commit()
                conn.close()
                st.success("患者信息更新成功！")
                del st.session_state.edit_patient_id
                del st.session_state.edit_patient_data
                time.sleep(2)
                st.session_state.display_patient = False
                st.rerun()
      
 


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
        gb.configure_column("skin_disease_name", header_name="皮肤病名称")
        gb.configure_column("skin_disease_history", header_name="皮肤病史")
        gb.configure_column("elderly_itch_related_disease", header_name="老年瘙痒症相关疾病")
        gb.configure_column("chronic_disease", header_name="慢性病")

        gridOptions = gb.build()

        response = AgGrid(
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

            response1 = AgGrid(
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
        p.skin_disease_name AS 皮肤病名称,
        p.skin_disease_history AS 皮肤病史,
        p.elderly_itch_related_disease AS 老年瘙痒症相关疾病,
        p.chronic_disease AS 慢性病,
        m.id AS 用药记录ID,
        m.antibiotic_name AS 抗生素名称,
        m.painkiller_name AS 止痛药名称,
        m.anticancer_name AS 抗癌药名称,
        m.antidepressant_name AS 抗抑郁药名称,
        m.skin_disease_medication AS 皮肤病用药名称,
        m.medication_date AS 用药日期
    FROM patients p
    INNER JOIN medications m ON p.id = m.patient_id
    """
    df = pd.read_sql_query(query, conn)
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

def pic_patient_medication_status():
    st.header("📊图表统计展示📈")
    pass


# Call the functions based on the selected app mode
if app_mode == "添加患者":
    add_patient()
elif app_mode == "导入患者数据":
    # import_patient_data()
    import_medications_data()
elif app_mode == "患者及用药情况":
    display_patients()
    edit_patient()
    # edit_medication()
elif app_mode == "患者信息查询":
    query_patient_medication()
    pic_patient_medication_status()
