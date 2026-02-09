import { ProductWithPrices, SourceEnum } from '../types/product';

// Keyword-to-image mapping: matches product names to relevant Unsplash photos
const keywordImages: [string[], string][] = [
  // Phones
  [['iPhone', 'Galaxy S2', 'Galaxy S1', 'Galaxy Z', 'Pixel', 'Xiaomi 14', 'Xiaomi 13', 'OnePlus', 'Sony Xperia', 'Motorola', 'Nothing Phone', 'Redmi Note'], 'photo-1511707171634-5f897ff02aa9'],
  [['Galaxy A', 'Redmi 13C', 'Galaxy S23'], 'photo-1598327105666-5b89351aff97'],
  // Headphones
  [['WH-1000', 'AirPods Max', 'Bose Quiet', 'Beats Studio', 'אוזניות over', 'Arctis', 'HyperX'], 'photo-1505740420928-5e560c06d30e'],
  [['AirPods Pro', 'AirPods 3', 'Galaxy Buds', 'JBL Live', 'Beats Fit', 'אוזניות True'], 'photo-1590658268037-6bf12f032f55'],
  // Speakers
  [['JBL Flip', 'JBL Charge', 'JBL Xtreme', 'Marshall', 'Bose SoundLink', 'רמקול נייד', 'Sonos Era'], 'photo-1608043152269-423dbba4e7e1'],
  [['Echo Dot', 'Echo Show', 'Nest Mini', 'Nest Hub', 'HomePod', 'רמקול חכם', 'מסך חכם'], 'photo-1543512214-318c7553f230'],
  // Tablets
  [['iPad'], 'photo-1544244015-0df4b3ffc6b0'],
  [['Galaxy Tab', 'Tab S9', 'Tab A9', 'Lenovo Tab', 'טאבלט'], 'photo-1561154464-82e9adf32764'],
  // Watches
  [['Apple Watch'], 'photo-1434493789847-2f02dc6ca35d'],
  [['Galaxy Watch', 'Garmin', 'Amazfit', 'Xiaomi Watch', 'שעון חכם', 'Fitbit', 'Whoop'], 'photo-1523275335684-37898b6baf30'],
  // TVs
  [['טלוויזי', 'OLED', 'QLED', 'Neo QLED', 'Mini LED'], 'photo-1593359677879-a4bb92f829d1'],
  // Gaming consoles
  [['PlayStation', 'PS5'], 'photo-1606144042614-b2417e99c4e3'],
  [['Xbox'], 'photo-1621259182978-fbf93132d53d'],
  [['Nintendo', 'Switch'], 'photo-1578303512597-81e6cc155b3e'],
  [['Quest', 'VR', 'משקפי'], 'photo-1622979135225-d2ba269cf1ac'],
  // Gaming peripherals
  [['DualSense', 'בקר', 'Controller'], 'photo-1592840496694-26d035b52b48'],
  [['עכבר גיימינג', 'Razer', 'Logitech G Pro'], 'photo-1527814050087-3793815479db'],
  // Cameras
  [['Canon', 'Sony Alpha', 'Nikon', 'מצלמ', 'GoPro'], 'photo-1516035069371-29a1b244cc32'],
  [['DJI', 'רחפן', 'Osmo'], 'photo-1473968512647-3e447244af8f'],
  // Storage & memory
  [['SanDisk', 'Samsung EVO', 'כרטיס זיכרון', 'microSD', 'SSD', 'NVMe', 'כונן', 'WD', 'Seagate', 'Kingston', 'Corsair Vengeance', 'RAM', 'זיכרון'], 'photo-1597838816882-4435b1977fbe'],
  // Chargers & power
  [['Anker', 'מטען', 'Belkin', 'PowerCore'], 'photo-1609091839311-d5365f9ff1c8'],
  // Network
  [['נתב', 'Mesh', 'Wi-Fi', 'TP-Link', 'ASUS RT', 'Deco'], 'photo-1558494949-ef010cbdcc31'],
  // NAS & UPS
  [['Synology', 'NAS', 'אל-פסק', 'APC'], 'photo-1558494949-ef010cbdcc31'],
  // Streaming & mic
  [['מיקרופון', 'Elgato', 'Blue Yeti', 'סטרימינג', 'StreamCam'], 'photo-1590602847861-f357a9332bbc'],
  // Docking
  [['CalDigit', 'Docking', 'עגינה'], 'photo-1625842268584-8f3296236761'],
  // Camera security
  [['מצלמת אבטחה', 'Tapo', 'Nest Cam', 'Ring', 'פעמון'], 'photo-1558002038-1055907df827'],
  // Apple Pencil & accessories
  [['Pencil', 'עט Apple'], 'photo-1585792180666-f7347c490ee2'],
  // Printers
  [['מדפסת', 'Epson', 'HP Laser', 'Brother', 'Canon PIXMA'], 'photo-1612815154858-60aa4c59eaa6'],

  // --- Computers ---
  [['MacBook Air'], 'photo-1517336714731-489689fd1ca8'],
  [['MacBook Pro'], 'photo-1517336714731-489689fd1ca8'],
  [['iMac'], 'photo-1527443224154-c4a3942d3acf'],
  [['Mac Mini', 'Mac Studio', 'Mac Pro'], 'photo-1591799264318-7e6ef8ddb7ea'],
  [['Dell XPS', 'Dell Inspiron', 'Dell Latitude'], 'photo-1588872657578-7efd1f1555ed'],
  [['ThinkPad', 'IdeaPad', 'Yoga', 'Lenovo'], 'photo-1525547719571-a2d4ac8945e2'],
  [['HP Spectre', 'HP Envy', 'HP Pavilion', 'HP Elite', 'HP Omen', 'HP Victus'], 'photo-1496181133206-80ce9b88a853'],
  [['ROG', 'VivoBook', 'ZenBook', 'TUF', 'ProArt', 'ASUS'], 'photo-1593642702821-c8da6771f0c6'],
  [['Acer', 'Nitro', 'Predator', 'Swift', 'Aspire'], 'photo-1587614382346-4ec70e388b28'],
  [['MSI'], 'photo-1593642702821-c8da6771f0c6'],
  [['Surface'], 'photo-1612462766104-a2a27ec7a2e3'],
  [['מסך', 'Monitor', 'UltraSharp', 'Odyssey', 'ViewFinity', 'ProArt PA', 'BenQ'], 'photo-1527443224154-c4a3942d3acf'],
  [['מקלדת', 'Keychron', 'BlackWidow', 'Corsair K'], 'photo-1587829741301-dc798b83add3'],
  [['עכבר', 'MX Master', 'MX Anywhere', 'M720', 'Arc Mouse'], 'photo-1527864550417-7fd91fc51a46'],
  [['מצלמת רשת', 'C920', 'Brio'], 'photo-1596566357666-43ce26240b8a'],
  [['Apple Studio Display', 'UltraFine'], 'photo-1527443224154-c4a3942d3acf'],
  [['Combo Touch', 'Magic Keyboard'], 'photo-1587829741301-dc798b83add3'],
  [['Odyssey G9'], 'photo-1616588589676-62b3d4ff6f04'],

  // --- Fashion ---
  [['Nike Air', 'Nike Dunk', 'Jordan', 'Nike Pegasus', 'Nike Revolution', 'Nike Court', 'Nike Metcon', 'Nike Mercurial', 'נעלי Nike'], 'photo-1542291026-7eec264c27ff'],
  [['Adidas Ultra', 'Adidas Stan', 'Adidas Super', 'Adidas Gazelle', 'Adidas Samba', 'Adidas Forum', 'Adidas NMD', 'Adidas Predator', 'נעלי Adidas'], 'photo-1518002171953-a080ee817e1f'],
  [['New Balance'], 'photo-1539185441755-769473a23570'],
  [['Puma', 'Converse', 'Vans', 'ASICS', 'Reebok'], 'photo-1460353581641-37baddab0fa2'],
  [['Timberland', 'מגפי'], 'photo-1520639888713-7851133b1ed0'],
  [['Dr. Martens'], 'photo-1520639888713-7851133b1ed0'],
  [['Birkenstock', 'כפכפ', 'Havaianas', 'סנדל', 'Teva', 'Crocs'], 'photo-1603487742131-4160ec999306'],
  [['חולצת Polo', 'חולצת Tommy', 'חולצת Lacoste', 'חולצת Calvin', 'חולצת Levi', 'חולצה מכופתרת'], 'photo-1596755094514-f87e34085b2c'],
  [['ג\'ינס', "ג'ינס"], 'photo-1542272604-787c3835535d'],
  [['מעיל', 'North Face', 'Columbia', 'Patagonia', 'בלייזר', 'מעיל גשם'], 'photo-1551028719-00167b16eac5'],
  [['סווטשירט', 'קפוצ\'ון', "קפוצ'ון"], 'photo-1556821840-3a63f95609a7'],
  [['מכנסי Nike', 'מכנסי Adidas', 'מכנסי אימון', 'טרנינג', 'מכנסיים קצרים'], 'photo-1562157873-818bc0726f68'],
  [['Samsonite', 'מזוודה', 'American Tourister'], 'photo-1565026057447-bc90a3dceb87'],
  [['תיק גב', 'Fjällräven', 'Herschel', 'JanSport', 'ילקוט'], 'photo-1553062407-98eeb64c6a62'],
  [['תיק צד', 'תיק יד', 'Michael Kors', 'Coach'], 'photo-1548036328-c9fa89d128fa'],
  [['חגורת', 'ארנק'], 'photo-1627123424574-724758594e93'],
  [['משקפי שמש', 'Ray-Ban', 'Oakley', 'Polaroid'], 'photo-1572635196237-14b3f281503f'],
  [['שעון Casio', 'שעון Daniel', 'שעון Fossil', 'שעון Tommy', 'שעון Michael'], 'photo-1524592094714-0f0654e20314'],
  [['כובע'], 'photo-1588850561407-ed78c334e67a'],
  [['גרביים', 'בוקסרים', 'חזייה', 'תחתון'], 'photo-1489987707025-afc232f7ea0f'],
  [['שמלת', 'שמלה'], 'photo-1572804013309-59a88b7e92f1'],
  [['חצאית'], 'photo-1583496661160-fb5886a0aaaa'],
  [['פיג\'מה', "פיג'מה"], 'photo-1489987707025-afc232f7ea0f'],
  [['נעלי בית', 'UGG'], 'photo-1603487742131-4160ec999306'],
  [['Skechers', 'נעלי הליכה'], 'photo-1460353581641-37baddab0fa2'],
  [['בגד ים', 'Speedo'], 'photo-1519315901367-f34ff9154487'],
  [['Hoka', 'Brooks', 'ON Cloud', 'Saucony', 'נעלי ריצה'], 'photo-1542291026-7eec264c27ff'],
  [['טייץ', 'חזייה ספורטיבית'], 'photo-1518459031867-a89b944bffe4'],

  // --- Home & Garden ---
  [['Dyson V', 'שואב אבק אלחוטי'], 'photo-1558317374-067fb5f30001'],
  [['Roborock', 'Roomba', 'iRobot', 'רובוט שואב', 'Dreame', 'Jet Bot'], 'photo-1667685271498-31e6c04bd5aa'],
  [['Nespresso', 'מכונת קפה'], 'photo-1559056199-641a0ac8b55e'],
  [['De\'Longhi', "De'Longhi", 'Breville', 'Philips 3200', 'Jura', 'אספרסו'], 'photo-1495474472287-4d71bcdd2085'],
  [['מדיח'], 'photo-1585771724684-38269d6639fd'],
  [['מקרר'], 'photo-1571175443880-49e1d25b2bc5'],
  [['מכונת כביסה', 'כביסה'], 'photo-1626806787461-102c1bfaaea1'],
  [['מייבש'], 'photo-1626806787461-102c1bfaaea1'],
  [['מטהר אוויר', 'Pure Cool', 'Air Purifier'], 'photo-1585771724684-38269d6639fd'],
  [['מזגן'], 'photo-1585771724684-38269d6639fd'],
  [['Philips Hue', 'תאורה חכמה', 'נורות', 'Lightstrip', 'TRÅDFRI'], 'photo-1558089687-5e5d6c7fb58e'],
  [['KitchenAid', 'Kenwood', 'מיקסר'], 'photo-1594385208974-2e75f8d7bb48'],
  [['Airfryer', 'Ninja', 'Tefal Acti', 'טיגון באוויר'], 'photo-1626082927389-6cd097cdc6ec'],
  [['Instant Pot', 'סיר לחץ'], 'photo-1585771724684-38269d6639fd'],
  [['מגהץ'], 'photo-1585771724684-38269d6639fd'],
  [['Weber', 'Traeger', 'גריל', 'מעשנ'], 'photo-1529193591184-b1d58069ecdd'],
  [['מזרן', 'Emma', 'Tempur'], 'photo-1631049307264-da0ec9d70304'],
  [['כרית'], 'photo-1631049307264-da0ec9d70304'],
  [['ספה', 'כורסת', 'POÄNG'], 'photo-1555041469-a586c61ea9bc'],
  [['שולחן אוכל'], 'photo-1617806118233-18e1de247200'],
  [['ארון', 'שידת'], 'photo-1595428774223-ef52624120d2'],
  [['סכינים', 'Zwilling'], 'photo-1593618998160-e34014e67546'],
  [['סט כלי מטבח', 'Tefal Ingenio'], 'photo-1556909114-f6e7ad7d3136'],
  [['מיקרוגל'], 'photo-1585771724684-38269d6639fd'],
  [['טוסטר', 'בלנדר', 'Vitamix', 'מכונת לחם'], 'photo-1594385208974-2e75f8d7bb48'],
  [['גלאי עשן', 'Nest Protect'], 'photo-1558002038-1055907df827'],
  [['מנעול חכם'], 'photo-1558002038-1055907df827'],
  [['שטיח'], 'photo-1556909114-f6e7ad7d3136'],
  [['מנורת'], 'photo-1507473885765-e6ed057ab6fe'],
  [['שולחן כתיבה', 'BEKANT'], 'photo-1518455027359-f3f8164ba6bd'],
  [['כיסא ארגונומי', 'Herman Miller', 'כיסא משרדי', 'MARKUS'], 'photo-1580480055273-228ff5388ef8'],
  [['מצעים', 'שמיכת'], 'photo-1631049307264-da0ec9d70304'],
  [['וילון'], 'photo-1513694203232-719a280e022f'],
  [['מפזר חום', 'מאוורר'], 'photo-1585771724684-38269d6639fd'],
  [['גוזם', 'גינ', 'צינור'], 'photo-1416879595882-3373a0480b5b'],
  [['סולם'], 'photo-1416879595882-3373a0480b5b'],
  [['קומקום', 'Kettle'], 'photo-1594385208974-2e75f8d7bb48'],
  [['OneBlade'], 'photo-1585771724684-38269d6639fd'],
  [['מראה', 'עציץ', 'שעון קיר'], 'photo-1513694203232-719a280e022f'],
  [['מגבות', 'מתלה', 'סל כביסה', 'ארגונית', 'מארגן', 'קופסאות'], 'photo-1556909114-f6e7ad7d3136'],

  // --- Sports & Health ---
  [['אופני הרים', 'אופני כביש', 'אופני עיר', 'אופניים חשמלי', 'אופני כושר', 'ספינינג', 'Peloton'], 'photo-1485965120184-e220f721d03e'],
  [['קורקינט'], 'photo-1589212987511-4a46db4a8c28'],
  [['הליכון'], 'photo-1576678927484-cc907957088c'],
  [['מכשיר חתירה', 'RowErg'], 'photo-1519311965067-36d3e5f33d39'],
  [['משקולות', 'קטלבל', 'ספת אימון', 'Pull-Up'], 'photo-1534438327276-14e5300c3a48'],
  [['מזרן יוגה', 'יוגה', 'גלגל יוגה', 'TRX', 'רצועות התנגדות', 'כדור כושר', 'מזרן כושר'], 'photo-1544367567-0f2fcb009e0b'],
  [['אגרוף', 'כפפות אגרוף', 'שק אגרוף'], 'photo-1549719386-74dfcbf7dbed'],
  [['כדורגל', 'מגני שוקיים', 'שער כדורגל', 'נעלי כדורגל'], 'photo-1575361204480-aadea25e6e68'],
  [['כדורסל'], 'photo-1546519638-68e109498ffc'],
  [['טניס', 'מחבט', 'פאדל', 'כדורי טניס', 'בדמינטון', 'רקטת'], 'photo-1554068865-24cecd4e34b8'],
  [['שולחן טניס', 'טניס שולחן'], 'photo-1609710228159-0fa9bd7c0827'],
  [['SUP', 'שנורקל', 'חליפת גלישה', 'שחייה', 'סנפיר', 'משקפי שחייה', 'מצוף', 'בגד ים Arena'], 'photo-1530053969600-caed2596d242'],
  [['סקי', 'קסדת סקי', 'משקפת סקי'], 'photo-1551698618-1dfe5d97d256'],
  [['מקלות הליכה', 'טיולים', 'Osprey', 'Deuter', 'אוהל', 'שק שינה', 'כירת גז', 'קמפינג'], 'photo-1551632811-561732d1e306'],
  [['בקבוק מים', 'Hydro Flask', 'CamelBak'], 'photo-1602143407151-7111542de6e8'],
  [['Garmin Edge', 'Wahoo', 'קסדת אופניים'], 'photo-1485965120184-e220f721d03e'],
  [['Theragun', 'עיסוי', 'Foam Roller'], 'photo-1544367567-0f2fcb009e0b'],
  [['משקל', 'Withings'], 'photo-1576678927484-cc907957088c'],
  [['מד לחץ', 'Omron', 'מד חום', 'Braun'], 'photo-1576091160550-2173dba999ef'],
  [['מברשת שיניים Oral', 'מברשת שיניים Philips', 'Waterpik', 'Sonicare'], 'photo-1576091160550-2173dba999ef'],
  [['מסכת שינה', 'מסאז', 'Shiatsu'], 'photo-1544367567-0f2fcb009e0b'],
  [['FreeStyle', 'סוכר'], 'photo-1576091160550-2173dba999ef'],
  [['ויטמין', 'חלבון', 'Quest Bar', 'BCAA', 'Creatine', 'מגנזיום', 'אומגה', 'מולטי'], 'photo-1556740758-90de374c12ad'],
  [['Hoka', 'Brooks', 'ON Cloud', 'Saucony', 'נעלי אימון', 'נעלי ריצה'], 'photo-1542291026-7eec264c27ff'],
  [['טייץ ריצה', 'חולצת ריצה', 'מכנסי אימון', 'חזייה ספורטיבית', 'Under Armour'], 'photo-1518459031867-a89b944bffe4'],
  [['חבל קפיצה', 'כלי שחייה'], 'photo-1534438327276-14e5300c3a48'],
  [['כפפות שוער'], 'photo-1575361204480-aadea25e6e68'],
  [['פטאנק', 'בוצ\'ה', "בוצ'ה"], 'photo-1416879595882-3373a0480b5b'],
  [['Fitbit', 'צמיד כושר'], 'photo-1523275335684-37898b6baf30'],

  // --- Kids & Babies ---
  [['עגלת', 'Bugaboo', 'Cybex Priam', 'Babyzen', 'UPPAbaby', 'Joie', 'Maclaren'], 'photo-1591370874773-6702e8f12fd8'],
  [['כיסא בטיחות', 'בוסטר', 'Cybex Sirona', 'Britax', 'Maxi-Cosi', 'BeSafe'], 'photo-1544776193-5ef4143eadb1'],
  [['מיטת תינוק', 'עריסה', 'מזרן מיטת תינוק'], 'photo-1522771739844-6a9f6d6c7ad5'],
  [['מוניטור', 'Nanit', 'Philips Avent SCD'], 'photo-1558002038-1055907df827'],
  [['נדנדה', '4moms', 'כיסא נדנדה', 'BabyBjörn Bliss'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['כיסא אוכל', 'Stokke Tripp', 'Chicco Polly'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['אמבטיה', 'Stokke Flexi'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['מנשא', 'Ergobaby', 'BabyBjörn Harmony'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['בקבוק', 'Dr. Brown', 'Philips Avent Natural', 'מעקר', 'NUK', 'כוס שתייה'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['משאבת חלב', 'Medela', 'Spectra', 'הנקה', 'Lansinoh'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['LEGO'], 'photo-1587654780013-04759610c472'],
  [['Playmobil', 'Barbie', 'Hot Wheels', 'Nerf', 'בובת', 'דינוזאור', 'מכונית שלט', 'רכבת עץ', 'מטבח משחק', 'כלי רופא'], 'photo-1596461404969-9ae70f2830c1'],
  [['Play-Doh', 'Crayola', 'פאזל', 'ציור', 'יצירה'], 'photo-1596461404969-9ae70f2830c1'],
  [['Monopoly', 'Settlers', 'Catan', 'Ticket to Ride', 'Codenames', 'Uno', 'Rummikub', 'משחק קופסה'], 'photo-1606092195730-5d7b9af1efc5'],
  [['אופניים לילדים', 'אופני איזון', 'Strider'], 'photo-1566004100477-7b7be4da9116'],
  [['קורקינט Micro'], 'photo-1566004100477-7b7be4da9116'],
  [['בריכה', 'טרמפולינה', 'מגלשה', 'נדנדה כפולה', 'ארגז חול'], 'photo-1566004100477-7b7be4da9116'],
  [['חיתולים', 'Pampers', 'Huggies', 'מגבונים'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['קרם החתלה', 'שמפו Johnson', 'סבון Mustela', 'קרם הגנה Mustela', 'Bepanthen'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['מזון תינוקות', 'Materna', 'Similac', 'דייסת', 'Gerber', 'חטיף לתינוק'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['צלחות', 'סט כלי אוכל', 'שער בטיחות', 'מגן פינות', 'תיק עגלה', 'Skip Hop'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['Sophie', 'מובייל', 'שטיח משחק', 'Tiny Love', 'התפתחותי'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['Carter\'s', "Carter's", 'בגד גוף', 'פיג\'מה לילדים', "פיג'מה לילדים", 'סט לידה', 'Aden'], 'photo-1515488042361-ee00e0ddd4e4'],
  [['ילקוט', 'Ergobag', 'קלמר', 'Smiggle'], 'photo-1553062407-98eeb64c6a62'],
  [['כיסא לימוד', 'שולחן לימוד'], 'photo-1580480055273-228ff5388ef8'],
  [['VTech', 'Toniebox', 'LeapFrog', 'Kindle Kids', 'Osmo', 'מיקרוסקופ', 'טלסקופ'], 'photo-1596461404969-9ae70f2830c1'],

  // --- Food & Drinks ---
  [['SodaStream', 'סודה', 'CO2', 'סירופ'], 'photo-1622483767028-3f66f32aef97'],
  [['קפסולות', 'Nespresso'], 'photo-1559056199-641a0ac8b55e'],
  [['קפה טחון', 'קפה פולים', 'Lavazza', 'Illy'], 'photo-1559056199-641a0ac8b55e'],
  [['תה', 'Twinings', 'Ahmad', 'מאצ\'ה', "מאצ'ה"], 'photo-1556679343-c7306c1976bc'],
  [['שמן זית', 'חומץ בלסמי'], 'photo-1474979266404-7f28db3f3150'],
  [['מלח', 'תבלינים', 'פפריקה', 'Schwartz'], 'photo-1532336414036-cf49da3ea048'],
  [['טחינה', 'חומוס', 'חלבה'], 'photo-1546069901-ba9599a7e63c'],
  [['שוקולד', 'Lindt', 'Ferrero', 'Toblerone', 'Godiva', 'Nutella'], 'photo-1481391319762-47dff72954d9'],
  [['חמאת בוטנים', 'דבש', 'ריבת', 'גרנולה', 'שיבולת שועל'], 'photo-1504674900247-0877df9cc836'],
  [['חלב שקדים', 'חלב שיבולת', 'Oatly', 'Alpro'], 'photo-1550583724-b2692b85b150'],
  [['יוגורט', 'גבינ', 'פרמזן', 'Philadelphia'], 'photo-1550583724-b2692b85b150'],
  [['פסטה', 'Barilla', 'De Cecco', 'אורז', 'קינואה', 'עדשים'], 'photo-1551462147-ff29053bfc14'],
  [['רוטב', 'Kikkoman', 'סריראצ\'ה', "סריראצ'ה", 'פסטו', 'קטשופ', 'מיונז', 'חרדל'], 'photo-1551462147-ff29053bfc14'],
  [['טונה', 'סרדינים', 'מלפפון', 'זיתים', 'עגבניות', 'רסק', 'שימורי'], 'photo-1551462147-ff29053bfc14'],
  [['Bamba', 'Bissli', 'ופל', 'Oreo', 'עוגיות', 'קרקר', 'Pringles', 'Doritos', 'ציפס', 'חטיף', 'פופקורן'], 'photo-1621939514649-280e2ee25f60'],
  [['אגוזי', 'שקדים', 'מיקס אגוזים', 'תמרים', 'פיסטוק'], 'photo-1608797178974-15b35a64ede9'],
  [['יין', 'Barkan', 'Yarden', 'Casillero'], 'photo-1510812431401-41d2bd2722f3'],
  [['בירה', 'Goldstar', 'Heineken', 'Corona'], 'photo-1535958636474-b021ee887b13'],
  [['וויסקי', 'Jameson', 'Glenfiddich', 'וודקה', 'Absolut', 'ג\'ין', "ג'ין", 'Hendrick'], 'photo-1569529465841-dfecdab7503b'],
  [['מים', 'Evian', 'San Pellegrino', 'מוגזים'], 'photo-1548839140-29a749e1cf4d'],
  [['מיץ', 'Red Bull', 'Monster', 'Coca-Cola', 'אנרגיה'], 'photo-1546171753-97d7676e4602'],
  [['מרק', 'פיצה קפואה', 'נאגטס', 'קפוא'], 'photo-1551462147-ff29053bfc14'],
  [['גלידה', 'Ben & Jerry', 'Häagen-Dazs'], 'photo-1497034825429-c343d7c6a68f'],
  [['מסטיק', 'סוכריות', 'Mentos', 'Orbit'], 'photo-1621939514649-280e2ee25f60'],
  [['קמח', 'סוכר', 'שמרים', 'אבקת אפייה', 'שוקולד שבבים', 'וניל', 'מייפל', 'קוקוס'], 'photo-1556909114-f6e7ad7d3136'],

  // --- Beauty ---
  [['בושם', 'Dior', 'Chanel', 'Versace', 'Hugo Boss', 'YSL', 'Paco Rabanne', 'Dolce', 'Marc Jacobs', 'Lancôme La Vie', 'Black Opium', 'Carolina Herrera', 'Gucci Bloom', 'Mugler', 'Victoria\'s Secret', "Victoria's Secret"], 'photo-1541643600914-78b084683601'],
  [['CeraVe', 'La Roche', 'Kiehl', 'קרם לחות', 'סרום', 'The Ordinary', 'Nuxe', 'Clinique Dramatically', 'BB Missha', 'קרם הגנה', 'Eucerin', 'אנטי אייג\'ינג', "אנטי אייג'ינג", 'Vichy', 'Estée Lauder Advanced', 'קרם עיניים', 'קרם צוואר', 'Clarins', 'Paula\'s Choice', "Paula's Choice"], 'photo-1556228578-0d85b1a4d571'],
  [['מסכת פנים', 'Glamglow', 'מסכות פנים', 'טונר', 'Pixi', 'Foreo', 'מברשת ניקוי', 'NuFACE', 'מיקרוקרנט'], 'photo-1596462502278-27bfdc403348'],
  [['מייק-אפ', 'Foundation', 'MAC Studio', 'Estée Lauder Double', 'Maybelline Fit'], 'photo-1512496015851-a90fb38ba796'],
  [['מסקרה', 'Lancôme Lash', 'Maybelline Lash'], 'photo-1512496015851-a90fb38ba796'],
  [['צלליות', 'Urban Decay', 'Charlotte Tilbury'], 'photo-1512496015851-a90fb38ba796'],
  [['שפתון', 'MAC Matte', 'YSL Rouge', 'גלוס', 'Fenty'], 'photo-1586495777744-4413f21062fa'],
  [['סומק', 'NARS', 'פודרה', 'Laura Mercier', 'קונסילר', 'אייליינר', 'Stila', 'עפרון גבות', 'Anastasia', 'פריימר', 'Smashbox', 'קיבוע'], 'photo-1512496015851-a90fb38ba796'],
  [['מסיר איפור', 'Bioderma'], 'photo-1556228578-0d85b1a4d571'],
  [['שמפו', 'מרכך', 'Moroccanoil', 'Olaplex', 'Kérastase', 'מסכת שיער'], 'photo-1522335789203-aabd1fc54bc9'],
  [['שמן שיער', 'שמן ארגן'], 'photo-1522335789203-aabd1fc54bc9'],
  [['מחליק שיער', 'GHD', 'Dyson Corrale'], 'photo-1522335789203-aabd1fc54bc9'],
  [['פן', 'Dyson Supersonic', 'Parlux', 'מסלסל', 'Airwrap'], 'photo-1522335789203-aabd1fc54bc9'],
  [['מכונת תספורת', 'Wahl'], 'photo-1621607512214-68297480165e'],
  [['מכונת גילוח', 'Braun Series', 'Philips Series', 'Philips S9', 'OneBlade QP6'], 'photo-1621607512214-68297480165e'],
  [['Gillette', 'סכיני גילוח', 'קרם גילוח'], 'photo-1621607512214-68297480165e'],
  [['דאודורנט', 'Old Spice', 'Dove'], 'photo-1556228578-0d85b1a4d571'],
  [['סבון גוף', 'קרם גוף', 'Nivea', 'קרם ידיים', 'L\'Occitane', "L'Occitane", 'ג\'ל רחצה', "ג'ל רחצה", 'Body Shop', 'פצצת אמבט', 'Lush', 'שמן גוף', 'Bio-Oil', 'מלח ים המלח', 'שיזוף'], 'photo-1571781926291-c477ebfd024b'],
  [['מברשת שיניים', 'Oral-B Vitality', 'משחת שיניים', 'Sensodyne', 'מי פה', 'Listerine', 'חוט דנטלי'], 'photo-1576091160550-2173dba999ef'],
  [['לק', 'OPI', 'Sally Hansen', 'מניקור', 'פדיקור', 'Scholl', 'ציפורניים'], 'photo-1604654894610-df63bc536371'],
  [['ווקס', 'Veet', 'IPL', 'Philips Lumea', 'Braun Silk', 'הסרת שיער'], 'photo-1598440947619-2c35fc9aa908'],
  [['סרום ריסים', 'RevitaLash'], 'photo-1512496015851-a90fb38ba796'],
];

// Fallback category images (used when no keyword match found)
const fallbackImages: Record<string, string> = {
  'אלקטרוניקה': 'photo-1468495244123-6c6c332eeece',
  'מחשבים': 'photo-1496181133206-80ce9b88a853',
  'אופנה': 'photo-1441986300917-64674bd600d8',
  'בית וגן': 'photo-1556909114-f6e7ad7d3136',
  'ספורט ובריאות': 'photo-1517836357463-d25dfeac3438',
  'ילדים ותינוקות': 'photo-1515488042361-ee00e0ddd4e4',
  'מזון ושתייה': 'photo-1546069901-ba9599a7e63c',
  'טיפוח ויופי': 'photo-1596462502278-27bfdc403348',
};

function getImage(productName: string, category: string): string {
  // Try to match product name against keywords
  for (const [keywords, photoId] of keywordImages) {
    for (const keyword of keywords) {
      if (productName.includes(keyword)) {
        return `https://images.unsplash.com/${photoId}?w=400`;
      }
    }
  }
  // Fallback to generic category image
  const fallback = fallbackImages[category] || 'photo-1468495244123-6c6c332eeece';
  return `https://images.unsplash.com/${fallback}?w=400`;
}

// Seeded random for consistent prices
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 9301 + 49297) * 49297;
  return x - Math.floor(x);
}

export function generateProducts(
  templates: [string, string, number][],
  category: string,
  startId: number
): ProductWithPrices[] {
  return templates.map((t, i) => {
    const [name, description, basePrice] = t;
    const id = startId + i;
    const seed = id * 7;

    const kspVar = 1 + (seededRandom(seed) * 0.1 - 0.02);
    const bugVar = 1 + (seededRandom(seed + 1) * 0.1 - 0.08);
    const zapVar = 1 + (seededRandom(seed + 2) * 0.1 + 0.01);

    const kspPrice = Math.round(basePrice * kspVar);
    const bugPrice = Math.round(basePrice * bugVar);
    const zapPrice = Math.round(basePrice * zapVar);

    const kspAvail = seededRandom(seed + 3) > 0.1;
    const bugAvail = seededRandom(seed + 4) > 0.15;
    const zapAvail = seededRandom(seed + 5) > 0.2;

    const prices = [
      { source: SourceEnum.KSP, price: kspPrice, currency: '₪', availability: kspAvail, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.BUG, price: bugPrice, currency: '₪', availability: bugAvail, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.ZAP, price: zapPrice, currency: '₪', availability: zapAvail, url: '#', last_updated: '2024-02-04' },
    ];

    const availPrices = prices.filter(p => p.availability).map(p => p.price);
    const lowest = availPrices.length > 0 ? Math.min(...availPrices) : undefined;
    const highest = availPrices.length > 0 ? Math.max(...availPrices) : undefined;
    const average = availPrices.length > 0 ? Math.round(availPrices.reduce((a, b) => a + b, 0) / availPrices.length) : undefined;

    const day = String((i % 28) + 1).padStart(2, '0');

    return {
      id,
      name,
      description,
      category,
      image_url: getImage(name, category),
      created_at: `2024-01-${day}`,
      prices,
      lowest_price: lowest,
      highest_price: highest,
      average_price: average,
    };
  });
}
