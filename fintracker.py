# import libraries
from datetime import datetime
import calendar
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import plotly.graph_objects as go
import database as db


page_title = "Income and Expense Tracker"
page_icon = ":heavy_dollar_sign:"
layout = "centered"
st.set_page_config(page_title = page_title,
                        page_icon = page_icon,
                        layout = layout)


# --- USER AUTHENTICATION ---
usernames = [st.secrets["DB_USER"]]
names = ['Ken']

hashed_passwords = [st.secrets["DB_PASS"]]

authenticator = stauth.Authenticate(names=names,
                                    usernames=usernames,
                                    passwords=hashed_passwords,
                                    cookie_name="webtoken_cookie",
                                    key="abcdef",
                                    cookie_expiry_days=0)

name, authentication_status, username = authenticator.login('Login','main')
# print(name, authentication_status, username)

if not authentication_status:
    st.error('Username/password is incorrect')

if authentication_status:
    if name[0]:
        st.write(f'Welcome *{name}*!')
        authenticator.logout('Logout','sidebar')

        # -----------SETTINGS---------
        incomes = ["Salary","Freelancing","Interest/Dividends","Tax Refunds","Gifts/Bonuses","Other Income"]

        # Fixed and Variable Expenses
            # Home, food, self care, utilities, transportation, insurance, healthcare
            # food (out), recreation, car, healthcare, taxes
        expenses = ["Rent",
                    "Groceries",
                    "Laundry", "Toiletries",
                    "Electricity", "Gas/Heating", "Water/Sewer","Trash/Pest Control","Internet/Telephone","Maintenance",
                    "Gasoline","Public Transit (Bus/Metro/Train/Carpool)","Regular Car Maintenance", "Parking Fees","Tolls", "Car Warranty","Car Registration/DMV fees",
                    "Health Insurance","Dental Insurance","Vision Insurance","Rental Insurance","Car Insurance",
                    "Out-of-Pocket","Co-Pays","Urgent Care","Specialty Care","Prescriptions",
                    "Breakfast (Out)","Lunch (Out)","Dinner(Out)","Snacks and Drinks (Out)",
                    "Travel/Vacation","Streaming/Subscriptions","Hobbies","Shopping (Shoes/Apparel)","Gifts for Others/Birthdays/Holidays","Newspapers/Books/Magazines","Charities",
                    "Variable Car Repairs",
                    "Variable Medical Bills",
                    "Taxes"]
        currency = "USD"

        # --------------------------
        st.title(page_title)


        # -------- DROPDOWN VALUES FOR SELECTING THE PERIOD ---
        years = [datetime.today().year, datetime.today().year-1]
        months = list(calendar.month_name[1:])


        # ------ DATABASE INTERFACE -----
        def get_all_periods():
            items = db.fetch_all_periods()
            periods = [item["key"] for item in items]
            return periods


        # ----- HIDE STREAMLIT STYLE ----
        hide_st_style = """
                        <style>
                        #MainMenu {visibility:hidden;}
                        footer {visibility:hidden;}
                        header {visibility:hidden;}
                        </style>
                        """
        st.markdown(hide_st_style, unsafe_allow_html=True)


        # -------- NAVIGATION MENU ---
        selected = option_menu(
            menu_title=None,
            options=["Data Entry","Data Visualization"],
            icons=["pencil-fill","bar-chart-fill"],
            orientation="horizontal"
        )

        # --------  INPUT AND SAVE PERIODS ------
        if selected == "Data Entry":
            st.header(f'Data Entry in {currency}')
            with st.form("entry_form", clear_on_submit = True):
                col1, col2 = st.columns(2)
                col1.selectbox("Select Month:", months, key="month")
                col2.selectbox("Select Year:", years, key ="year")


                with st.expander("Income"):
                    for income in incomes:
                        st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)

                with st.expander("Expenses"):
                    for expense in expenses:
                        st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)

                with st.expander("Comment"):
                    comment = st.text_area("",placeholder="Enter a comment here ...")

                submitted = st.form_submit_button("Save Data")
                if submitted:
                    period = str(st.session_state["year"]) + "--" + str(st.session_state["month"])
                    incomes = {income: st.session_state[income] for income in incomes}
                    expenses = {expense: st.session_state[expense] for expense in expenses}
                    db.insert_period(period,incomes,expenses,comment)
                    st.write('Data Saved!')

        if selected == "Data Visualization":
            # --- PLOT PERIODS ---
            st.header("Data Visualization")
            with st.form("saved_periods"):
                period = st.selectbox("Select Period:", get_all_periods())
                submitted = st.form_submit_button("Plot Period")
                if submitted:
                    period_data = db.get_period(period)
                    comment = period_data.get("comment")
                    expenses = period_data.get("expenses")
                    incomes = period_data.get("incomes")

                    #Create metrics
                    total_income = sum(incomes.values())
                    total_expense = sum(expenses.values())
                    remaining_budget = total_income - total_expense
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Income", f"{total_income} {currency}")
                    col2.metric("Total Expense", f"{total_expense} {currency}")
                    col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
                    st.text(f"Comment: {comment}")

                    # Creating Sankey
                    income_labels = list(incomes.keys()) + ["Total Income"]
                    expense_labels = list(expenses.keys())
                    all_labels = income_labels + expense_labels
                    source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
                    target = [len(incomes)] * len(incomes) + [all_labels.index(expense) for expense in expenses.keys()]
                    value = list(incomes.values()) + list(expenses.values())

                    # Data to dict, dict to sankey
                    link = {"source":source, "target":target, "value":value}
                    node = {"label":all_labels, "pad":20, "thickness":30}
                    data = go.Sankey(link=link, node=node)

                    # Plotting the Sankey
                    fig = go.Figure(data)
                    fig.update_layout(margin={"l":0,"r":0,"t":5,"b":5})
                    # If you want to show in a separate tab
                    # fig.show()
                    # Show in the same appls
                    st.plotly_chart(fig,use_container_width=True)


                    print(income_labels)
                    print(len(income_labels))
                    res = '' in income_labels
                    print(f'empty string in income labels: {res}')

                    print(expense_labels)
                    print(len(expense_labels))
                    res2 = '' in expense_labels
                    print(f'empty string in expense labels: {res2}')

                    print(all_labels)
                    print(len(all_labels))

