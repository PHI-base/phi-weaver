#see current file in vim-folder, that I use as start-up script, it is on H-drve with autoconnect
# beneath just for learning purposes and may not have up-to-date drive information

taskkill /im "lync.exe" /f          
net use A: \\salt\fusa_guarana /persistent:no >nul
net use B: \\salt\fusarium /persistent:no >nul
REM C reserved
REM D reserved 
REM E reserved 
REM F reserved 
REM G reserved 
REM H reserved 
REM I reserved 
net use J: \\salt\fg_snrk1_asn /persistent:no >nul
net use L: \\salt\phi_mc_enl /persistent:no >nul
net use M: \\salt\metabol /persistent:no >nul
net use N: \\salt\cyp51_lanos /persistent:no >nul
net use O: \\salt\fus_culmorum /persistent:no >nul
net use Q: \\salt\fus_culmorum2 /persistent:no >nul
net use P: \\salt\fustarget /persistent:no >nul
net use R: \\salt\wheatdisease /persistent:no >nul
net use S: \\salt\phibasefair2019 /persistent:no >nul
net use T: \\salt\fus_duf /persistent:no >nul
net use U: \\salt\fung_trafomu /persistent:no >nul
net use V: \\salt\fusarium-2 /persistent:no >nul
net use W: \\salt\b63_uv /persistent:no >nul   
net use X: \\salt\fus_video /persistent:no >nul   
#net use Y: \\salt\pathbio /persistent:no >nul  
net use Z: \\salt\fungi_rawdat /persistent:no >nul
REM \\salt\fus_duf #Elsbieta Janowska-Sedja
REM \\salt\phibasefair2019 #Phibase grant
REM \\salt\fustarget #Natalia Martins
REM \\salt\cyp51_lanos #Jieru Fan, Hans Cools
REM \\salt\metabol  #Rohan Lowe
REM \\salt\phi_mc_enl  #phi-base early 
REM \\salt\bioinf_resources
REM \\salt\bioinf_training
REM \\salt\wp_lap_meeting_recordings   #for lab meeting videos
REM \\salt\kinase   #with Melanie Jubault's Bayer files, 2010-2016.
REM \\salt\arabidopsis       #2010 BBSRC Ara granta/Amy    Alayne Cuzick/Kerry Maguire
REM \\salt\arabidopsis2
REM WPT drive   Kosty Kanuka
REM \\salt\fus_effec_ck   Claire Kanja   2019-2023
REM fus_effec_cw   Catherine Walker  ~2019 end
REM fus_receptor   Natalia Martins
REM fus_secretom   Neil Brown?
REM fus_video      Martin Urban
REM fusarium       #very first drive
REM fusarium-2     #2nd early drive
REM fusiamage      #?????? Neil Brown
REM fus_target     #Natalia Martins drive
REM rnai_kk        #kostya syngenta  info and RNA data
REM wheatdisease  #Kim Hammond-Kosack
REM wpt            #kostya   shared wpt files
REM fung_trafomu  #Fusarium protocols
REM fungi_rawdat  # Oses, virtualbox, raw genomes
REM fghigs_embrapa      # Ana Machado 2019
REM fg_higs      # Ana Machado 2019
REM fus_com1     Laura Baggelay 2017-2021  
REM mgram2      Mycosphaerella
REM mycog      Mycosphaerlla
REM fus_sysbio_ek2020    #for Erika Kroll - PHD
REM \\salt\fg_snrk1_asn #for Nigel Halford BBSRC grant 4/2022-3/2026 + Navneet Kaur
REM \\salt\takeall /persistent:no >nul
REM \\salt\steromic   #drive Microscopy Kirsty Halsey
REM \\salt\fus_protease   #2021/2022 USDA-Purdue-RRES project 'Engineering plant resistance'
REM 2023-01-10 \\salt\phi-canto ; linux accessible at cd /home/data/phi-canto 
REM 2023-01-10 \\salt\phi-base_5 ; linux accessible at cd /home/data/phi-base_5
REM
REM 2023-03-21 \\salt\wp_lab_meeting_recordings     #Lawrnce Bramham is owner
REM 2023-03-21 \\wpt_fructans      1TB unsused data                 #Kim HK is owner        
REM 2023-09-21 \\salt\fructan-wpt-2023     #500GB   #Wanxin Chen is owner
REM 2023-03-29 \\salt\cen2_laboratory_support
REM 2021-11-00 \\salt\fusariumpangenome_secretome  #Amber Stevens work with Mark Darino; owner Keywan Hassani-Pak, Dan Smith also has access. There is almost nothing on the drive.
REM 2023-11-02 \\salt\protease-fus-2023_rp10740-10, drive for Reynaldi Darma, US project, linux drive
REM 2023-11-11 \\salt\WheatPath_LabMgmt_RP10796-14  #owner Laurence Bramham     # in use for LAB PROTOCOLS AND LAB MANAGEMENT
REM 2024-09-28 \\salt\fus_antioxidants   #Noah Walker, PhD, Rotation1
REM The appdata folder is found in c:\users\[username] so in your case it will be c:\users\urbanm, on occasion the folder will have a .rres on the end.
REM The appdata folder is a hidden folder so you will need to go in to the organize menu and select folder and search options 
REM and then in the view tab turn on ‘Show hidden files, folders  and drives’
REM obo-edit config files and Aspera needs deleting; software needs to be closed first!
REM taskkill /IM your-program-name.your-program-extnesion /T /F        # /T=all child processes, /IM = process name , /F=forecuflly
REM taskkill /IM "C:\Program Files (x86)\StarLeaf\StarLeaf\StarLeaf.exe" /T /F

rmdir /s /q "C:\Users\urbanm\AppData\Roaming\Macromedia"
rmdir /s /q "C:\Users\urbanm\AppData\Roaming\MySQL"
rmdir /s /q "C:\Users\urbanm\AppData\Roaming\inkscape"
rmdir /s /q "C:\Users\urbanm\AppData\Roaming\Windows\Cookies"
rmdir /s /q "C:\Users\urbanm\AppData\Roaming\Notepad++"
rmdir /s /q "C:\\Users\urbanm\AppData\Roaming\Skype"    
rmdir /s /q "C:\\Users\urbanm\AppData\Roaming\Corel"    
rmdir /s /q "C:\\Users\urbanm\AppData\Roaming\Adobe\Adobe Photoshop CS5.1"    
rmdir /s /q "C:\\Users\urbanm\AppData\Roaming\Adobe\Dreamweaver CS5.5"    
rmdir /s /q "C:\\Users\urbanm\AppData\Roaming\Dropbox"
rmdir /s /q "C:\\Users\urbanm\AppData\Roaming\Genstat"
rmdir /s /q "C\\Users\urbanm\AppData\Roaming\Programs\Aspera"    
echo hello.bat 
start /d "H:\\MU_current.exe"

