from sqlalchemy import create_engine

# engine = create_engine('sqlite:///G:\\DB\\inteltool.db', echo=False)
engine = create_engine('mysql://user:password@localhost/inteltool?charset=utf8', echo=False)
zkillboard_id = "Your Name (user@domain.com)"
evemarketdata_id = "Eve Char Name"
