import os
from sqlalchemy import *
from flask import Flask,render_template,request,g,url_for,redirect,flash
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__)

DATABASE_USERNAME = "lw2980"
DATABASE_PASSWRD = "3316"
DATABASE_HOST = "34.148.107.47"  # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"

#
# This line creates a database engine that knows how to connect to the URI above.
#

engine = create_engine(DATABASEURI)
@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route("/")
@app.route('/home')
def home_page():
   ####get policy:
   policy_command="select * from daily_travel_policy;"
   cursor = g.conn.execute(text(policy_command))
   policy = []
   for result in cursor:
       policy.append(list(result))
   cursor.close()
   for i in policy:
       i[0] = i[0].strftime("%Y/%m/%d")


   ######get price:
   price_command="select to_char(datetime, 'MM-DD'), avg(price) from flight group by to_char(datetime, 'MM-DD') order by to_char(datetime, 'MM-DD'); "
   cursor = g.conn.execute(text(price_command))
   date=[]
   price_f = []
   for i in cursor:
       date.append(i[0])
       price_f.append(float(i[1]))
   cursor.close()


   ####get hotel
   hotel_command="select hotel_id, age, star_rank from hotel;"
   cursor = g.conn.execute(text(hotel_command))
   hid=[]
   age=[]
   rank=[]
   for i in cursor:
       hid.append(i[0])
       age.append(float(i[1]))
       rank.append(int(i[2]))
   cursor.close()
   #### for text box
   num_cust_command="select count(*) from customer;"
   cursor = g.conn.execute(text(num_cust_command))
   num_cust=[]
   for i in cursor:
       num_cust.append(i[0])
   cursor.close()
   num_cust = num_cust[0]
#  ########
   cursor = g.conn.execute(text("select count(*) from travel;"))
   Trav_times=[]
   for i in cursor:
       Trav_times.append(i[0])
   cursor.close()
   Trav_times = Trav_times[0]

# ######
   cursor = g.conn.execute(text("select count(*) from airport;"))
   num_airport=[]
   for i in cursor:
       num_airport.append(i[0])
   cursor.close()
   num_airport = num_airport[0]
# #####
   cursor = g.conn.execute(text("select sum(area) from airport;"))
   area=[]
   for i in cursor:
       area.append(i[0])
   cursor.close()
   area = area[0]
# ####
   cursor = g.conn.execute(text("select count(*) from hotel;"))
   num_hotel=[]
   for i in cursor:
       num_hotel.append(i[0])
   cursor.close()
   num_hotel = num_hotel[0]
# ####
   cursor = g.conn.execute(text("select star_rank,count(*) from hotel group by star_rank having star_rank=5;"))
   num_5hotel = []
   for i in cursor:
       num_5hotel.append(i[1])
   cursor.close()
   num_5hotel = num_5hotel[0]
   #####male and female
   cursor = g.conn.execute(text("select gender, count(*) from customer group by gender;"))
   gender = []
   num_gender=[]
   for i in cursor:
       gender.append(i[0])
       num_gender.append(i[1])
   cursor.close()






   return render_template('home.html',gender=gender,num_gender=num_gender,
                          num_cust=num_cust,Trav_times=Trav_times,
                          num_airport=num_airport,
                          area=area,
                          num_hotel=num_hotel,
                          num_5hotel=num_5hotel,
                          policy=policy,date=date,price_f=price_f,hid=hid,age=age,rank=rank)


@app.route("/city",methods = ["Post","Get"])
def city_page():
    city_command="select  name , average_visits, consumption_level, transit_type  from city;"
    cursor = g.conn.execute(text(city_command))
    city=[]
    for i in cursor:
        city.append(i)

    return render_template('city.html',city=city)

@app.route("/flight",methods = ["Post","Get"])
def flight_page():
    if request.method=='POST':
        size=request.form.get('airline-size')
        sd=request.form.get('date-start')
        ed=request.form.get('date-end')
        price=request.form.get('max-price')


        check_command = "select * from flight  where datetime between '{sd}' and '{ed}' and aircraft_type='{size}' and price<={price} order by price " .format(sd=str(sd),ed=str(ed),size=size,price=price)
        cursor = g.conn.execute(text(check_command))
        re = []
        for result in cursor:
            re.append(list(result))
        cursor.close()
        for i in re:
            i[2]=i[2].strftime("%Y/%m/%d/%H:%M")
            i[3]=i[3].strftime("%H:%M")
            i[4]=float(i[4])
            i[6]=float(i[6])

        if len(re) == 0:
            return render_template('flight.html',error='No matched flight')
        else:
            print(re)
            return render_template('flight.html',re=re)

    return render_template('flight.html')


@app.route('/book', methods=['POST','GET'])
def process_booking():
    name = request.form['name']
    password = request.form['password']
    airline = request.form['airline']
    get_uid_coomand = "select customer_id from customer where name='%s' " % (name)
    cursor = g.conn.execute(text(get_uid_coomand))
    uid=[]
    for i in cursor:
        uid.append(list(i))
    cursor.close()
    uid=uid[0][0]


    # Check if the password is correct (you need to implement this)

    if check_password(name,password):
        get_id_coomand="select airline_id from airlines where name='%s' "%(airline)
        cursor = g.conn.execute(text(get_id_coomand))
        id=[]
        for i in cursor:
            id.append(list(i))
        cursor.close()

        id=id[0][0]
        book_command="INSERT INTO book VALUES ('%s','%s')"%(uid,id)
        g.conn.execute(text(book_command))
        g.conn.commit()
        g.conn.close()
        return '', 200
    else:
        return '', 401






    # Code to save the booking details goes here





@app.route("/login",methods = ["Post","Get"])
def login_page():
    if request.method=='POST':
        name=request.form.get('username')
        password=request.form.get('password')
        if check_password(name,password):
           preference_command="select preference.* from customer left join preference on customer.customer_id=preference.customer_id where name ='%s' "%(name)
           cursor = g.conn.execute(text(preference_command))
           preference_re=[]
           for i in cursor:
               preference_re.append(i)
           cursor.close()
           preference_re=list(preference_re[0])
           if preference_re[1]=='yes':
               preference_re[1]='others'
           else:
               preference_re[1] = 'yourself'
           ####total book
           book_command="select t.name , count(*) as num from (select a.name as name from customer  as c left join book as b on c.customer_id=b.customer_id left join airlines as a on a.airline_id=b.airline_id where c.name='%s') as t group by t.name "%(name)
           book_re=[]
           cursor = g.conn.execute(text(book_command))

           for i in cursor:
               book_re.append(list(i))
           cursor.close()
           ### ########travel
           travel_command = " select date ,c1.name, c2.name, flight_id  from travel as tr left join city as c1 on c1.city_id=tr.departure_city_id left join city as c2 on c2.city_id =tr.arrival_city_id where tr.customer_id in(select customer_id from customer where name='%s')"%(name)
           travel_re = []
           cursor = g.conn.execute(text(travel_command))

           for i in cursor:
               travel_re.append(list(i))
           cursor.close()

           return render_template('user.html',usr=name, preference_re= preference_re,book=book_re,travel=travel_re)
        else:
          return render_template('login.html',msg='wrong password')
    else:
        return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        #############firstly , get the total # of users
        total_user_command="select count(customer_id) as num from customer;"
        cursor = g.conn.execute(text(total_user_command))
        num = []
        for i in cursor:
            num.append(list(i))
        num=int(num[0][0])
        cursor.close()

        ####################
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if len(username) < 5:
            return render_template("register.html",error1='error:length less than 5')

        elif password1 != password2:
            return render_template("register.html",error2='error:Password not matched')
        else:
            ########insert into customer
            ###INSERT INTO customer VALUES (1, ‘Selina Doe’, ‘212W 91st’, 6143086700, ‘selina@outlook.com’, 22, ‘female’, ‘student’, 10000);
            id=num+1
            address=request.form.get('address')
            phone=request.form.get('phone')
            mail=request.form.get('email')
            age=request.form.get('age')
            gender=request.form.get('gender')
            rev=request.form.get('revenue')
            budget=request.form.get('Budget')
            occupation=request.form.get('occupation')
            cust_command="INSERT INTO customer VALUES ({id}, '{name}', '{address}', {phone}, '{mail}', {age}, '{gender}', '{occupation}', {rev});".format(id=id,name=username,address=address,phone=phone,mail=mail,age=age,gender=gender,occupation=occupation,rev=rev)
            g.conn.execute(text(cust_command))
            g.conn.commit()
            g.conn.close()
            ####Insert into password
            psw_command="INSERT INTO password VALUES('{name}','{psw}');".format(name=username,psw=password2)
            g.conn = engine.connect()
            g.conn.execute(text(psw_command))
            g.conn.commit()
            g.conn.close()
            ####Insert into preference
            #INSERT INTO preference VALUES (1, 'yes' , 'leisure'  , ' warm '  , 2100 ,  'airbnb' , 5 );
            tra_follower=request.form.get('travelfollowers')
            purpose=request.form.get('purpose')
            climate=request.form.get('Climate')
            accomodation=request.form.get('accomodation')
            dur=request.form.get('Travel Duration')
            pre_command="INSERT INTO preference VALUES({id},'{tra_follower}','{purpose}','{climate}',{budget},'{accomodation}',{dur});".format(id=id,tra_follower=tra_follower,purpose=purpose,climate=climate,budget=budget,accomodation=accomodation,dur=dur)
            g.conn = engine.connect()
            g.conn.execute(text(pre_command))
            g.conn.commit()
            g.conn.close()
            return render_template("register.html", succ='Congrats:Account created successfully!')


    return render_template("register.html")
def check_password(name, password):
    check_command="select * from password where name ='%s' and password='%s'"%(name, password)
    cursor = g.conn.execute(text(check_command))
    names = []
    for result in cursor:
        names.append(result[0])
    cursor.close()
    print(names)
    if len(names) == 0:

        return False
    else:
        return True








if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000)






# @app.route('/about/<username>')
# def about_page(username):
#     return f'<h1>About page of {username}</h1>'
# @app.route('/market')
# def market_page():
#     items = [
#         {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
#         {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
#         {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
#     ]
#     return render_template('market.html',items=items)