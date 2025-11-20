from db.database import Base, engine
import models.customer  # import every model module
import models.conversation
import models.document

print("About to create tables on:", engine.url)
Base.metadata.create_all(bind=engine)
print("Done.")
