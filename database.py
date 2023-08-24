# import os
from deta import Deta
# from dotenv import load_dotenv
import streamlit as st

# Load the env var
# load_dotenv(".env")

# DETA_KEY = os.getenv("DETA_KEY")

DETA_KEY = st.secrets["DETA_KEY"]

# Initialize w/ project key
deta = Deta(DETA_KEY)

db = deta.Base("monthly_reports")

def insert_period(period, incomes, expenses, comment):
    """Returns the report on successful creation, otherwise raise an error"""
    return db.put({"key":period,"incomes":incomes,"expenses":expenses,"comment":comment})


def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items

def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)

