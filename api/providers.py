from datetime import datetime,timedelta
from venv import logger
from .db import db
studRef = db.collection("students")
agentRef = db.collection("Agents").document("agentInfo")
agentStat = db.collection("Agents").document("agentStat")
admin = db.collection("Admin")
def AddStudent(agentRef,userInfo):
    ref = studRef.document(userInfo["userId"])
    user = ref.get()
    if not user.exists:
        ref.set({**userInfo,"agentRef":agentRef,"approved":False})
        
def GetAgentTeleId(student):
    ref = studRef.document(student).get()
    if ref.exists:
        agent_referal_code = ref.to_dict()["agentRef"]
        agentInfo = agentRef.get().to_dict()
        if agent_referal_code in agentInfo:
            return [agentInfo[agent_referal_code]["teleid"],agent_referal_code]  
        return ['',agent_referal_code] 
    return ["",""]

def ApproveStudent(student):
    agent_referal_code = GetAgentTeleId(student)[1]
    studRef.document(student).update({"approved":True})
    try:
        if agent_referal_code:
            agent_data = agentStat.get().to_dict()
            
            if agent_referal_code not in agent_data:
                return {"ok": False, "error": "Referral code not found in agent data"}
            
            cur_agent = agent_data[agent_referal_code]
            date = format_date(datetime.now())
            
            cur_agent['timestamp'].append(date)
            cur_agent['ownStud'] += 1
            
            TWeek = this_week(cur_agent['timestamp'])
            
            BASE_AMOUNT = 400
            PERCENTAGE = 0.25
            BONUS_AMOUNT = 10
            WEEKLY_BONUS_THRESHOLD = 5
            
            total_money = BASE_AMOUNT * PERCENTAGE 
            if not TWeek % 5:
                total_money += (TWeek % WEEKLY_BONUS_THRESHOLD) * BONUS_AMOUNT
            cur_agent['totalAmount'] += total_money
            cur_parent = cur_agent['parent']

            ind = 0
            while ind < 2 and cur_parent in agent_data and cur_parent:
                agent_payment = 100 * PERCENTAGE
                agent_data[cur_parent]['totalAmount'] += agent_payment
                agent_data[cur_parent]['agentStud'] += 1
                total_money += agent_payment
                cur_parent = agent_data[cur_parent]['parent']
                ind += 1
            
            agentStat.update(agent_data)
            admin.document(agent_referal_code).set({'money': BASE_AMOUNT - total_money, 'timeStamp': date})
        print("successfully sending agents")
        return {"ok": True, 'message': "send"}
    except KeyError as e: 
        logger.error(f"KeyError: {str(e)}")
        return {"ok": False, "error": f"KeyError: {str(e)}"}
    except Exception as e:
        print("The error while sending transaction")
        logger.error(f"An error occurred: {str(e)}")
        return {"ok": False, "error": str(e)}

def GetStudent(stId):
    ref = studRef.document(stId).get()
    if ref.exists:
        return ref.to_dict()["userName"]
def GetStudentInfo(stId):
    ref = studRef.document(stId).get()
    if ref.exists:
        return ref.to_dict()
    return {}
def setStudentInfo(stId,info):
    fieldToUpdate,value = info
    ref = studRef.document(stId).update({fieldToUpdate:value})
def this_week(dates):
    
    current_date = datetime.now()

    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    count = 0
    for date_str in dates:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if start_of_week <= date <= end_of_week:
            count += 1

    return count

def format_date(date):
    year = date.year
    month = str(date.month).zfill(2)  # Month is zero-indexed, so add 1
    day = date.day  # Get the day of the month without leading zero

    return f"{year}-{month}-{day}"
def setLastId(teleid):
    ref = studRef.document("lastmessage")
    ref.set({"teleid":teleid})       
def getLastId():
    ref = studRef.document("lastmessage").get().to_dict()
    return ref["teleid"]  
message = r"""ስለ Victory Tutorial ከተማሪዎች የሚነሱ ጥያቄዎች🤔🤔🤔?።
 
1\. *Tutorial በ*video *ወይስ በ* note *ነው የሚሰጠው?*
 
🧩ይህ ጥያቄ በተደጋጋሚ የሚጠየቅ እና እኛም በተደጋጋሚ ስንመልሰው የቆየነው ጥያቄ ቢሆንም አሁንም ድረስ የብዙ ተማሪዎች ጥያቄ ነው።
Victory tutorial የሚሰጥበት መንገድ በ video ኣይደለም\! ነገር ግን ከvideo በተሻለ እና ጊዜ ቆጣቢ በሆነ መንገድ እንዲሁም ለሁሉም አይነት ተማሪ በሚሆን መንገድ በ note የተዘጋጀ ሲሆን ይህም አማርኛ እና እንግሊዘኛ ቋንቋዎች በማዋሃድ የቀረበ ሲሆን  ተማሪዎች ሸምዳጅ ሳይሆን conceptual እንዲሆኑ ታስቦ የተዘጋጀ ነው። እንዲሁም ተማሪዎች የመሰላቸት ስሜት ውስጥ እንዳይገቡ በማሰብ በሚያዝናና ቀልብን በሚገዛ መንገድ ተዘጋጅቷል።

 🧩ይህ መንገድ ያልተለመደ እና አዲስ የ tutorial አሰጣጥ በመሆኑ ከ video በተሻለ ጊዜን ቆጣቢ እና በተሻለ ማብራርያ የቀረበ መሆኑ የተለየ እና ተመራጭ ያደርገዋል። ስለዚህ victoryን ስትጠቀሙ ጊዜያችሁን ትቆጥባላችሁ እንደገና ደግሞ በደንብ ተረድታችሁ ለ entrance exam ብቁ ትሆናላሁ ። በአንድ ድንጋይ ሁለት ወፍ ማለት ይሄ አይደል\!

2\. *አሁን* victory’*ን ብቀላቀል ያለፉኝን* chapter’*ኦች ማግኝት እችላለሁ?*

🎯ይህ ጥያቄ ሌላኛው የተማሪዎች ጥያቄ ሲሆን በአጭሩ ለመመለስ ያህል
አንድ ተማሪ በየትኛውም ጊዜ ወደ ቪክትሪ ቢቀላቀል ከመጀመርያው ጀምሮ ያሉትን chapter’ኦች በሙሉ ምንም ሳይጎል ማግኘት እና ማጥናት ይችላል። ከናንተ ሚጠበቀው ስልካችሁን ወደ ላይ scroll ማድረግ ብቻ ነው። አምልጦኛል የሚል ጭንቀት አያሳስባችሁ ሁሉም አለ\! 

👉ነገር ግን ቀድማችሁ ብተገቡ ተመራጭ ያደርገዋል። ምክንያቱም በጊዜ ጥናታችሁን እንድትጀምሩ እና ጊዜ የለኝም ከሚል ጭንቀት ነጻ እንድትሆኑ ያደርጋቹሃል። ከዚ በተጨማሪም ቪክትሪን ለተቀላቀሉ ልጆች እንዴት ማጥናት እንዳለባቸው እና ለፈተና ስነልቦናዊ ዝግጅት እንዲኖራቸው የምንረዳቸው ይሆናል።

3\. *አሁን* victory’*ን ተቀላቅዬ ለ* entrance exam *በቀረው አጭር ጌዜ ውስጥ መዘጋጀት እችላለሁ?*

🎯ይህ ጥያቄ የብዙዎች ጥያቄ ብቻ ሳይሆን ጭንቀትም ጭምር ነው ። ቅድም እንደነገርኳችሁ የvictory tutorial ከአላማዎቹ ውስጥ እንዴት ተማሪውን በአጭር ጊዜ ውስጥ በተሻለ መረዳት እና የትምህርት ጥራት ለፈተና ማዘጋጀት እንችላለን ብለን ስልሆነ የተነሳነው ፤ እንደውም አልደርስም፣ አልጨርሰም ብላችሁ በተስፋ መቁረጥ ውስጥ ላላችሁ🙇‍♀️🙇 ተማሪዎች በእጅጉን ትልቅ መፍትሄ ነው። ስለዚህ በንደዚህ አይነት ጭንቀት ውስጥ ያላችሁ ተማሪዎች victory ጋር ጊዜ አላችሁ።

 🎯ከ 9\-12 ያሉትን በአጭር ጌዜ ውስጥ እንዲያልቁ ተደርገው ስለተዘጋጁ ምንም እንዳታስቡ👱‍♀️🧓 ።

4\. *Tutorial’ኡ የተዘጋጀው እንዴት ነው?*

🧩የ victory tutorial የተዘጋጀው ቅድም እንደነገርኳችሁ በ note ሲሆን አዘገጃጀቱ ከ 9\-10 በ old curriculum እና የ11\- 12 በ new curriculum በአጠቃላይ 9\-12 ያሉት የ maths የ physics እና chemistry ትምህርቶችን በመጭመቅ የተዘጋጀ ነው።

5\. *Tutorial’ኡን በ* telegram *የምናገኘው እንዴት ነው?*

🧩አንድ ተማሪ victory’ን ሲቀላቀል tutorial’ኡን የሚከታተለው telegram ላይ በ private channel ሲሆን ትምህርቶቹ በ note መልክ ሆነው ስለተዘጋጁ አንዴ ካወረዳችሁት በኋላ በማንኛውም ሰኣት መጠቀም ትችላላችሁ።

🧩 Wi\-Fi ለማታገኙ ተማሪዎችም በቀላሉ የ 5 ብር ካርድ ሞልታችሁ ብቻ ሁሉንም እዛው ማውረድ እና offline አድርጋችሁ መጠቀም ትችላላችሁ። ስለዚህ እንደ YouTube video የግድ የ internet አገልግሎት ወይም online መሆን አይጠበቅባችሁም ማለት ነው።

በመጨረሻም እቺን ግጥም ተጋበዙልን\.\.\.

የማያልቁ ገፆች በአጭር ተተንትነው
ረዥም ፅሁፎች በአጭር ተበትነው
በቀላል አረዳድ በቀላል ሁኔታ
ብዙ ጥያቄዎች ከነመልስ በተርታ
ውጤትን ለመስቀል ከልብ ከፈለጉ
የ victory\-ን tutor አሁን join ያርጉ።

 
🎯ምን እየጠበቃችሁ ነው ታዳ ቶሎ ተቀላቅላቹ እርፍ ነው እንጂ \!\!\!

*VICTORY IS A STATE OF MIND*\!"""

natural = r"""
*Victory Academy* ስትቀላቀሉ የምታገኟቸው የትምህርት አይነቶች

📙*English*
 📗*Maths*
  📕*Physics*
   📓*Chemistry \&*
    📘*Biology  ናቸው። *
👉ከነፃ የ5አመት የኢንትራንስ ጥያቄ ከነተብራራ መልሶቻቸው ጋር

‼️እነዚህን ሁሉ በአንድ ጊዜ የክፍያ ስርዐት ብቻ ካለምንም ተጨማሪ ክፍያ የምታገኙ ይሆናል
"""
social = r"""
*Victory Academy* ስትቀላቀሉ የምታገኟቸው የትምህርት አይነቶች

📙*English*
📗*Maths*
  📕*Geography*
   📓*History \&*
    📘*Economics   ናቸው።*
👉ከነፃ የ5አመት የኢንትራንስ ጥያቄ ከነተብራራ መልሶቻቸው ጋር

‼️እነዚህን ሁሉ በአንድ ጊዜ የክፍያ ስርዐት ብቻ ካለምንም ተጨማሪ ክፍያ የምታገኙ ይሆናል
"""
Cbe = r'''[🗒]
💳 *ንግድ ባንክ  \= 1000400328677 ይትባረክ መብራቱ*

*Victory Academy* ሙሉ አመቱን የሚሰጠውን አገልግሎት *በ 399 ብር ብቻ* ካለምንም ተጨማሪ ክፍያ ታገኛላቹ

📌*ክፍያውን* የፈፀማቹት
🏦ባንክ ሄዳቹ ከሆነ የከፈላቹበትን ደረሰኝ ፎቶ አንስታቹ 
📲በmobile Banking ከሆነ  የከፈላቹበትን ደረሰኝ screenshot እዚው ቴሌግራም Bot ላይ ላኩልን

👉የላካቹልንን ፎቶ በሰዐታት ውስጥ አረጋግጠን ወደ Victory Academy የምትቀላቀሉ ይሆናል

‼️*ማሳሰቢያ*:\- ከሁለት ቀን በላይ ያለፈው ደረሰኝ አንቀበልም። ስለዚህ በቻላቹት አቅም ክፍያውን በፈፀማቹበት ቀን ደረሰኙን ላኩልን


*VICTORY IS A STATE OF MIND*\!\!'''
teleBirr = r'''💳*ቴሌብር  \= 0992839147 ይትባረክ መብራቱ*

*Victory Academy* ሙሉ አመቱን የሚሰጠውን አገልግሎት *በ 399 ብር ብቻ* ካለምንም ተጨማሪ ክፍያ ታገኛላቹ

📌*ክፍያውን* ከፈፀማቹ በኋላ የከፈላቹበትን ደረሰኝ screenshot እዚው ቴሌግራም Bot ላይ ላኩልን

👉*የላካቹልንን ፎቶ* በሰዐታት ውስጥ አረጋግጠን ወደ Victory Academy የምትቀላቀሉ ይሆናል

‼️*ማሳሰቢያ*:\- ከሁለት ቀን በላይ ያለፈው ደረሰኝ አንቀበልም። ስለዚህ በቻላቹት አቅም ክፍያውን በፈፀማቹበት ቀን ደረሰኙን ላኩልን


*VICTORY IS A STATE OF MIND*\!\!'''
awashBank = r'''\[🗒\]
💳*በአዋሽ ባንክ \= 013201261675000 ይትባረክ መብራቱ*

*Victory Academy* ሙሉ አመቱን የሚሰጠውን አገልግሎት *በ 399 ብር ብቻ* ካለምንም ተጨማሪ ክፍያ ታገኛላቹ

📌*ክፍያውን* የፈፀማቹት
🏦ባንክ ሄዳቹ ከሆነ የከፈላቹበትን ደረሰኝ ፎቶ አንስታቹ 
📲በmobile Banking ከሆነ የከፈላቹበትን ደረሰኝ screenshot እዚው ቴሌግራም Bot ላይ ላኩልን

👉የላካቹልንን ፎቶ በሰዐታት ውስጥ አረጋግጠን ወደ Victory Academy የምትቀላቀሉ ይሆናል

‼️*ማሳሰቢያ*:\- ከሁለት ቀን በላይ ያለፈው ደረሰኝ አንቀበልም። ስለዚህ በቻላቹት አቅም ክፍያውን በፈፀማቹበት ቀን ደረሰኙን ላኩልን


*VICTORY IS A STATE OF MIND*\!\!'''
EBirr = r'''💳 *E \- Birr  \= 0914633658 ይትባረክ መብራቱ*

Victory Academy ሙሉ አመቱን የሚሰጠውን አገልግሎት በ 399 ብር ብቻ ካለምንም ተጨማሪ ክፍያ ታገኛላቹ

📌*ክፍያውን* ከፈፀማቹ በኋላ የከፈላቹበትን ደረሰኝ screenshot እዚው ቴሌግራም Bot ላይ ላኩልን

👉የላካቹልንን ፎቶ በሰዐታት ውስጥ አረጋግጠን ወደ Victory Academy የምትቀላቀሉ ይሆናል

‼️ *ማሳሰቢያ*:\- ከሁለት ቀን በላይ ያለፈው ደረሰኝ አንቀበልም። ስለዚህ በቻላቹት አቅም ክፍያውን በፈፀማቹበት ቀን ደረሰኙን ላኩልን


*VICTORY IS A STATE OF MIND*\!\!'''
Banks = {
    'CBE':Cbe, 'Tele Birr':teleBirr, 'Awash Bank':awashBank, 'E-Birr':EBirr
}
