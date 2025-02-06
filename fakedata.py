import streamlit as st
import pandas as pd
import sqlite3
import random
from faker import Faker
from datetime import datetime

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('patients.db')
    return conn

fake = Faker('zh_CN')

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
        test_data.append((name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation ,is_chronic_disease, skin_disease_name, skin_disease_history, elderly_itch_related_disease, ','.join(chronic_disease),care_provider))
    return test_data

def generate_test_medications(num_records=10):
    medications_data = []
    for _ in range(num_records):
        patient_id = random.randint(1, num_records)  # Assuming patient IDs are sequential starting from 1
        antibiotic_name = fake.word()
        painkiller_name = fake.word()
        anticancer_name = fake.word()
        antidepressant_name = fake.word()
        skin_disease_medication = fake.word()
        medication_date = fake.date_between(start_date="-1y", end_date="today")
        
        medications_data.append((patient_id, antibiotic_name, painkiller_name, anticancer_name, antidepressant_name, skin_disease_medication, medication_date))
    return medications_data

def import_test_data():
    test_data = generate_test_data()
    medications_data = generate_test_medications(len(test_data))
    
    conn = get_db_connection()
    
    # Insert patient data
    conn.executemany('''INSERT INTO patients (name, gender, birth_date, age, contact, address, height, weight, insurance_type, care_status, monthly_income, cooperation, is_chronic_disease,skin_disease_name, skin_disease_history, elderly_itch_related_disease, chronic_disease,care_provider) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', test_data)
    
    # Insert medication data
    conn.executemany('''INSERT INTO medications (patient_id, antibiotic_name, painkiller_name, anticancer_name, antidepressant_name, skin_disease_medication, medication_date) VALUES (?, ?, ?, ?, ?, ?, ?)''', medications_data)
    
    conn.commit()
    conn.close()
    st.success("测试数据导入成功！")
    
import_test_data()