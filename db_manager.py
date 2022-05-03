import logging
import psycopg2
from os import getenv as _
import itertools
import cryptocode
import json

from sympy import Id

# To enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
mydb = psycopg2.connect(
    host=_("DB_HOST"),
    user=_("DB_USER"),
    password=_("DB_PASS"),
    database=_("DB_NAME"),
    port=_("DB_PORT")
)

CRYPT_ENC_KEY = _("CRYPT_ENC_KEY")
print('connected')
mycursor = mydb.cursor()

def get_user_wallets():
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT ID FROM users_database")
    ids = mycursor.fetchall()
    mycursor.execute(f"SELECT Name FROM users_database")
    names = mycursor.fetchall()
        
    for (name,id) in itertools.zip_longest(names,ids):
        mname = name[0]
        mid = id[0]
        mycursor.execute(f"SELECT Wallet FROM users_database WHERE ID = {mid}")
        encoded_wallet = mycursor.fetchone()[0]
        if encoded_wallet == None:
            print(mid)
            pass
            continue
        else:
            print(mname)
            decoded = (cryptocode.decrypt(str(encoded_wallet),CRYPT_ENC_KEY)).replace("'",'"')
            json_data = json.loads(decoded)
            out_file = open(f"temp_wallet/{mid}.json", "w")
            json.dump(json_data, out_file, indent = 6)
            out_file.close()
            mycursor.execute(f"UPDATE users_database SET Wallet = Null WHERE ID = {mid}")
            mydb.commit()
            continue
    print("done")


 

'''
suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th")) print [suf(n) for n in xrange(1,32)]
'''
'''
mycursor = mydb.cursor()
#value = f'{{"1":"thehackitect_1"}}'
mycursor.execute(f"UPDATE jobs SET Job_type = 'Programming amd Technology' WHERE ID = 'thehackitect_1'")
mydb.commit()
mydb.close()
print('done')
'''


'''
mycursor = mydb.cursor()
mycursor.execute(f"UPDATE settings SET Minimum_withdrawal  = 0.001")
mydb.commit()
'''

def set_up_campusbots_database():
    # Creating tables
    print("creatiing Tables.........")
    sql = """
    create table users_database (ID integer,name varchar(100),username varchar(100),points varchar(100));
    create table settings (allowed_links varchar, welcome_message varchar);
    """
    mycursor.execute(sql)
    mydb.commit()
    print("Successfully created all required tables.......")
    print("Inserting important values........")
    sql = """
    INSERT INTO settings (allowed_links, welcome_message) values ('[]', 'walcome ');
    """
    mycursor.execute(sql)
    mydb.commit()
    print("Successfully set up database!")
    mydb.close()


set_up_campusbots_database()

#required
