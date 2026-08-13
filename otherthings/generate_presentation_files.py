import os
import pandas as pd

# Klasör yolu
folder_path = "final_sunumu_için_dosyalar"
os.makedirs(folder_path, exist_ok=True)

# 1. Klasik Toksiklik Testi
file_1 = pd.DataFrame({
    'yorum': [
        "Bugün hava gerçekten çok güzel, parkta yürüyüş yapmak iyi gelecek.",
        "Bu makale için çok teşekkür ederim, gerçekten faydalı bilgiler var.",
        "Toplantı saatini 14:00 olarak güncelledik, bilginize.",
        "Sen gerçekten tam bir aptalsın, hayatımda senin kadar gerizekalı birini görmedim.",
        "Kapa çeneni artık, senin o gereksiz fikirlerini kimse dinlemek istemiyor.",
        "Defol git buradan, kimse seni bu grupta istemiyor zavallı herif.",
        "Thank you for the quick response, I will review the documents tonight.",
        "I respectfully disagree with your conclusion, but I appreciate the analysis.",
        "Please let me know if you need any further assistance with this project.",
        "You are an absolute idiot, shut your mouth and never post again.",
        "Go fuck yourself, you are a disgusting waste of space.",
        "Nobody cares about your pathetic opinion, loser.",
        "Harika bir gün geçirmenizi dilerim, iyi çalışmalar.",
        "Seni bulursam çok kötü yapacağım, hesabını soracağım.",
        "Bütün yabancılar iğrençtir ve ülkelerine geri gönderilmelidir."
    ]
})

# 2. Dostane Argo ve Pozitif Bağlam (V1/V2'nin hata yaptığı, V5.2+'nin başarılı olduğu durumlar)
file_2 = pd.DataFrame({
    'yorum': [
        "Oğlum manyak mısın lan bu kadar hızlı nasıl birinci oldun helal olsun!",
        "Şerefsizim çok iyi düşünmüşsün efsane olmuş bu proje, tebrikler!",
        "Ulan harbi helal olsun, bunu tek başına yapabileceğine inanmıyordum.",
        "Vay hayvan vay, yine sınavdan en yüksek notu kapmışsın!",
        "Manyak herif, bu kadar kısa sürede bu tasarımı nasıl bitirdin?",
        "Pislik seni, yine en güzel yeri kendine ayırtmışsın, kıskandım.",
        "Ulan sen ne komik adamsın, gülmekten karnıma ağrılar girdi.",
        "You absolute madman, I can't believe you managed to pull that off! Sick job.",
        "This code is ridiculously good, you crazy bastard.",
        "Holy shit, that was the most amazing guitar solo I've ever heard!",
        "You son of a bitch, count me in for this adventure!",
        "Damn right, you earned that promotion, keep killing it!",
        "Fuck yeah, we finally passed the final test!",
        "You lucky bastard, how did you score those front-row tickets?",
        "You absolute legend, thank you so much for helping me move."
    ]
})

# 3. İnce Sarkazm ve Zararsız İroni (Sadece V5.02 / V5.22 Cascade modellerinin yakalayabildiği durumlar)
file_3 = pd.DataFrame({
    'yorum': [
        "Harika bir iş çıkardın gerçekten, projeyi tek başıma bu kadar hızlı batıramazdım.",
        "Bu üstün vizyonunla Silikon Vadisi'ne CEO olman an meselesi kardeşim, tebrikler.",
        "Aynen kanka kesin öyledir, sen anlattıysan kesinlikle doğrudur, hiç şüphem yok.",
        "Sana laf anlatmaktansa duvara konuşsam duvar en azından dinliyor gibi yapar.",
        "Sayende iki saat fazladan mesai yaptım, ne kadar düşünceli bir insansın.",
        "Tabii canım, sen varken Google'a veya yapay zekaya ne gerek var.",
        "Bravo, yine en yanlış kararı en kısa sürede vermeyi başardın.",
        "Oh, brilliant idea. Let's push this untested code directly to production on a Friday.",
        "Wow, it only took you three weeks to fix a single typo. We should throw a parade.",
        "What a profound insight, you must be the smartest person in this empty room.",
        "I'm so glad you decided to bless us with your incompetence today.",
        "Thank you for demonstrating exactly how not to write a python script.",
        "It's fascinating how you consistently manage to lower the bar of expectation.",
        "I would agree with you, but then we'd both be wrong.",
        "Your feedback is as useful as a screen door on a submarine."
    ]
})

# 4. Zorlu Sınır Durumlar ve Hata Analizi (Tüm modelleri zorlayan uç durumlar)
file_4 = pd.DataFrame({
    'yorum': [
        "Herkes hak ettiğini bulur, umarım sen de tez zamanda bulursun.",
        "Bu grupta bazı insanların zeka seviyesi gerçekten yerlerde sürünüyor.",
        "O kadar akıllısın ki, etrafındakilerin kendini aptal hissetmesine neden oluyorsun.",
        "Bütün bu suçların arkasında belli bir kesimin olduğu gün gibi ortada.",
        "Yine harika bir makale yazmışsın, gözlerim yaşardı okurken.",
        "Senin gibi birinin bu pozisyona gelmesi gerçekten ülkenin durumunu özetliyor.",
        "Watch your back, you never know who might be behind you.",
        "I hope you have a wonderful day, unlike the day you gave me.",
        "Some groups of people simply do not have the capacity for high-level work.",
        "Let's see if your code actually works this time, I won't hold my breath.",
        "It is amazing how you talk so much while saying absolutely nothing.",
        "I hope you get exactly what you deserve.",
        "Dur bakalım, bir daha karşıma çıktığında hesabını soracağım.",
        "Bu projenin liderliğini bir kadına vermek ne kadar mantıklı tartışılır.",
        "Vay arkadaş, bu oyun ne kadar kafa açıyor lan!"
    ]
})

# CSV olarak kaydet (projedeki gibi sep=';' ile)
file_1.to_csv(os.path.join(folder_path, "01_temel_siniflandirma_testi.csv"), index=False, sep=';', encoding='utf-8-sig')
file_2.to_csv(os.path.join(folder_path, "02_dostane_argo_ve_pozitif_baglam.csv"), index=False, sep=';', encoding='utf-8-sig')
file_3.to_csv(os.path.join(folder_path, "03_ince_sarkazm_ve_zararsiz_ironi.csv"), index=False, sep=';', encoding='utf-8-sig')
file_4.to_csv(os.path.join(folder_path, "04_zorlu_sinir_durumlar_ve_hata_analizi.csv"), index=False, sep=';', encoding='utf-8-sig')

print("Dosyalar başarıyla oluşturuldu:")
for f in os.listdir(folder_path):
    print(f"- {os.path.join(folder_path, f)}")
