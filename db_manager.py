import logging
import psycopg2
from os import getenv as _
import itertools
import cryptocode
import json

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
    create table users_database (ID integer,Name varchar(100),Balance varchar(100),Matric varchar(100),Phone varchar(100),Email varchar(100),Bio varchar(100),Status varchar(100),Warnings varchar(100),Wallet VARCHAR(7000),Referral_id varchar(100),Referrals varchar(100),Referral_earnings varchar(100));
    create table admins (ID integer,fund varchar(100),super_admin varchar(100),ban_user varchar(100),make_admin varchar(100),pause_bot varchar(100),check_user varchar(100),job_pricing varchar(100),advert_pricing varchar(100),removing_users varchar(100),bank_detailing varchar(100), email_advert_Pricing varchar(100),minimum_withdrawal varchar(100), litecoin_pricing varchar(100));
    create table settings (advert_price varchar(100), job_price varchar(100), bank_details varchar(100), report_email varchar(100), maintenance varchar(100), max_warning varchar(100),email_advert_price varchar(100),wallet VARCHAR(7000),minimum_withdrawal varchar(100),litecoin_earning_price varchar(100));
    create table freelancer (ID integer,username varchar(100),rank varchar(100),specializations varchar(100),jobs varchar);
    create table jobs (ID varchar,status varchar(100),Price varchar(100),Biders varchar,Title varchar,Description varchar,Job_type varchar);
    """
    mycursor.execute(sql)
    mydb.commit()
    print("Successfully created all required tables.......")
    print("Inserting important values........")
    sql = """
    INSERT INTO admins (ID,fund,super_admin,ban_user,make_admin,pause_bot,check_user,job_pricing,advert_pricing,removing_users,bank_detailing,email_advert_Pricing,minimum_withdrawal,litecoin_pricing) VALUES (1233125771, 'True', 'True', 'True', 'True', 'True', 'True', 'True', 'True', 'True', 'True','True','True','True');
    INSERT INTO settings (advert_price, job_price, bank_details, report_email, maintenance, max_warning,Email_advert_price,minimum_withdrawal,litecoin_earning_price) values (0, 0, 'none', 'thehackitect.bots@gmail.com', 'False', 2, 0,0.001,0.00005);
    INSERT INTO freelancer (ID,username,rank,specializations,jobs) VALUES (1233125771, 'thehackitect', '3', '[1,2,3,4,5,6,7,8,9,10]', '[thehackitect_1]');
    INSERT INTO jobs (ID,Status,Price,Biders,Title,Description,Job_type) values ('thehackitect_1', 'Open', '5000','[1233125771]','Programming','This is the description on this project','Programming amd Technology');
    """
    mycursor.execute(sql)
    mydb.commit()
    print("Successfully set up database!")
    mydb.close()


set_up_campusbots_database()