
# # ---------------------- Define schemas of Data -------------------------

# # ------------------------ Processing --------------------------------

def llm2sql(parameter):
    import openai
    import pyodbc
    import pandas as pd
    import sqlalchemy as sa
    import json
    import re

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.sql import text
    from sqlalchemy import text


    #Parameter

    ### PART 1: CONNECT TO SQL SERVER
    # Connect to SQL Server
    userquest = parameter

    server = 'xznozrobo3funm76yoyaoh75wm-frugwj4xeune3pikgul3sab7tu.datawarehouse.pbidedicated.windows.net' 
    database = 'loading_data'
    # server = 'xznozrobo3funm76yoyaoh75wm-qhke725ydcietlngqiyrfxa75u.datawarehouse.pbidedicated.windows.net' 
    # database = 'testSQL'
    username = "api@oilgas.ai"
    password = 'Muz42633'
    driver = 'ODBC Driver 17 for SQL Server'  

    # connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=no&Authentication=ActiveDirectoryPassword'
    params = 'Driver=' + driver + ';Server=' + server + ',1433;Database=' + database + ';Uid={' + username + '};Pwd={' + password + '};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=ActiveDirectoryPassword'
    
    openai.api_key = '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'

    # 1. Kết nối đến cơ sở dữ liệu sử dụng pyodbc
    # ### PART 2: DEFINE FUNCTIONS
    # engine = create_engine(connection_string, echo=True, connect_args={'auto_commit': True}, fast_executemany=True)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    Session = sessionmaker(bind=engine)
    session = Session()

    # Define the query using SQLAlchemy's text function
    query = text(f"SELECT * FROM [{database}].[INFORMATION_SCHEMA].[COLUMNS]")

    # In danh sách các tên cột
    # Execute the query and fetch the results
    results = session.execute(query).fetchall()
    # Close the session
    session.close()

    # Print the results
    # for row in results:
    #     print(row)
    df = pd.DataFrame(results)

    df = df[['TABLE_CATALOG', 'TABLE_SCHEMA', 'TABLE_NAME', 'COLUMN_NAME', 'DATA_TYPE']]
    table_names_to_keep = ['dbo']
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df['TABLE_SCHEMA'].isin(table_names_to_keep)]
    filtered_df['TABLE_NAME'] = '['+ filtered_df['TABLE_CATALOG'] + '].[' + filtered_df['TABLE_SCHEMA'] + '].[' + filtered_df['TABLE_NAME'] + ']'

    # Drop the original 'TABLE_CATALOG', 'TABLE_SCHEMA', and 'TABLE_NAME' columns
    filtered_df = filtered_df[['TABLE_NAME', 'COLUMN_NAME', 'DATA_TYPE']]
    filtered_df = filtered_df.rename(columns={
        'TABLE_NAME':'A', 
        'COLUMN_NAME':'B',
        'DATA_TYPE': 'C'})
    schema = filtered_df.to_json(orient='records', lines=True)

    # # Print the JSON data
    # print(schema)

    #userquestion
    userquest_input = userquest

    #Modeling for the question
    openai.api_key = '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'
    context = f'You are data analyst who knows well about oil field and well with the data base about well log has schema like this:{schema}, for A is Table name in the system, B is column name, and C is Column data type. Any column named WELL_UWI means well name.Generate only SQL function to answer user question, basing on schema. Dont explain anything further or ask back. Dont give columns name that does not appear in schema'

    response = openai.ChatCompletion.create(
        model= "gpt-4", #"gpt-3.5-turbo-16k", 
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": "You are a helpful assistant."},
            {"role": "system", "content": "SELECT COUNT(DISTINCT WELL_UWI) FROM [loading_data].[dbo].[wellinfo]"},
            {"role": "user", "content": userquest_input}
        ]
    )

    # Extract and print the assistant's response
    message_content = response.choices[0].message['content']
    print(message_content)

    # engine = create_engine(connection_string, echo=True, connect_args={'auto_commit': True}, fast_executemany=True)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    Session2 = sessionmaker(bind=engine)
    session = Session2()
    
    

    sql = text(message_content)


    deploy = "yes"
    # Execute the query and fetch the results
    if deploy == 'yes':
        results = session.execute(sql).fetchall()
    # Close the session
    session.close()

    #from decimal import Decimal
    print("kết quả querry")
    print(type(results))
    print(results)
    # Chuyển danh sách thành chuỗi
    results = [str(item) for item in results]
    results = " ".join(results)
    results = re.sub("[^0-9a-zA-Z ,.-]", "", results)
    results = results.rstrip(", ")

    print("kết quả final querry")
    print(results)
    friendlyresponse = openai.ChatCompletion.create(
        model= "gpt-4", #"gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": f'you are the template maker. Your role is creating template to answer user question about the database. Answer in general answer ONLY TEXT DO NOT INCLUDE SQL function, WELL NAME, CURVE NAME'},
            {"role": "user", "content": userquest_input}
        ]
    )
    message_content = friendlyresponse.choices[0].message['content']
    message_content = re.sub(r'\{.*?\}', '', message_content)
    message_content = re.sub(r'\[.*?\]', '', message_content)
    message_content = re.sub(r'\<.*?\>', '', message_content)

    # Remove extra spaces and comma if needed
    message_content = message_content.strip().strip(',')
    message_content = message_content.rstrip(", ")
    message_content = message_content.rstrip(".").rstrip() + ":"

    print("message_content_friendly")
    print(type(message_content))
    custom_result = {}
        # Ghép hai chuỗi
    custom_result = message_content + " " + results
    print (custom_result)

    result_in_json = json.dumps(custom_result)
    return result_in_json