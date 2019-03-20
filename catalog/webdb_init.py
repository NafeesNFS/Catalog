from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///websites.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete WebsiteName if exisitng.
session.query(WebsiteName).delete()
# Delete ToolName if exisitng.
session.query(ToolName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="Nafees Akhtar",
             email="beingnafeesnfs@gmail.com")
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample Websites
Website1 = WebsiteName(name="Morzilla",
                       user_id=1)
session.add(Website1)
session.commit()

Website2 = WebsiteName(name="Microsoft",
                       user_id=1)
session.add(Website2)
session.commit

Website3 = WebsiteName(name="Alibaba Group",
                       user_id=1)
session.add(Website3)
session.commit()

Website4 = WebsiteName(name="Opera",
                       user_id=1)
session.add(Website4)
session.commit()

# Populare a tool
# Using different users for tools
Tool1 = ToolName(name="FireFox",
                 discription="Web Browser",
                 year="2002",
                 founder="Morzilla",
                 date=datetime.datetime.now(),
                 websitenameid=1,
                 user_id=1)
session.add(Tool1)
session.commit()

Tool2 = ToolName(name="MS Word",
                 discription="Word Processor ",
                 year="1983",
                 founder="Microsoft",
                 date=datetime.datetime.now(),
                 websitenameid=2,
                 user_id=1)
session.add(Tool2)
session.commit()

Tool3 = ToolName(name="Opera",
                 discription="Web Browser",
                 year="1995",
                 founder="Opera",
                 date=datetime.datetime.now(),
                 websitenameid=3,
                 user_id=1)
session.add(Tool3)
session.commit()

Tool4 = ToolName(name="Maxthon",
                 discription="Cloud Browser",
                 year="2002",
                 founder="Maxthon Limited",
                 date=datetime.datetime.now(),
                 websitenameid=4,
                 user_id=1)
session.add(Tool4)
session.commit()

session.commit()

print("Your database has been inserted!")
