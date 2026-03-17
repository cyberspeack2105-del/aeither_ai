# MongoDB Atlas Migration Guide (தமிழ் / Tamil)

இந்த வழிகாட்டி உங்கள் லோக்கல் MongoDB தரவுத்தளத்தை (Local Database) MongoDB Atlas கிளவுட்க்கு (Cloud) மாற்ற உதவும்.

## Step 1: MongoDB Atlas கணக்கை உருவாக்குதல் (Create Account)
1. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) இணையதளத்திற்குச் சென்று ஒரு இலவச கணக்கை உருவாக்கவும்.
2. ஒரு புதிய **Project**-ஐ உருவாக்கவும்.
3. **Build a Database** என்பதைக் கிளிக் செய்து, **M0 Free Tier**-ஐத் தேர்ந்தெடுக்கவும்.

## Step 2: Database User-ஐ உருவாக்குதல்
1. இடது பக்க மெனுவில் **Database Access** என்பதைக் கிளிக் செய்யவும்.
2. **+ Add New Database User** என்பதைக் கிளிக் செய்யவும்.
3. ஒரு பயனர் பெயர் (Username) மற்றும் கடவுச்சொல்லை (Password) உருவாக்கவும். (இதை குறித்து வைத்துக்கொள்ளவும்).

## Step 3: வையர்லெஸ் அணுகல் (Network Access)
1. **Network Access** என்பதைக் கிளிக் செய்யவும்.
2. **Add IP Address** என்பதைக் கிளிக் செய்து, **Allow Access From Anywhere (0.0.0.0/0)** என்பதைத் தேர்ந்தெடுக்கவும்.

## Step 4: Connection String-ஐப் பெறுதல்
1. **Database** பக்கத்திற்குச் சென்று, உங்கள் கிளஸ்டரில் உள்ள **Connect** பட்டனைக் கிளிக் செய்யவும்.
2. **Drivers** என்பதைத் தேர்ந்தெடுக்கவும்.
3. அங்கு தோன்றும் "Connection String"-ஐ நகலெடுக்கவும் (Copy).
   * எடுத்துக்காட்டு: `mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`

## Step 5: .env கோப்பை புதுப்பித்தல்
உங்கள் `backend/.env` கோப்பில் லோக்கல் URL-க்குப் பதிலாக புதிய Atlas URL-ஐச் சேர்க்கவும்:
```env
MONGO_URL=mongodb+srv://your_username:your_password@cluster0.mongodb.net/chatbot?retryWrites=true&w=majority
```

## Step 6: தரவை மாற்றுதல் (Data Migration)
நீங்கள் லோக்கல் தரவை அட்லஸிற்கு மாற்ற விரும்பினால், **MongoDB Compass**-ஐப் பயன்படுத்தி 'Export' மற்றும் 'Import' செய்யலாம்.

---

இந்த மாற்றத்திற்குப் பிறகு, உங்கள் ஆப் ஆன்லைன் மேகக்கணியில் (Cloud) தரவைச் சேமிக்கும்!
