import pandas as pd
import matplotlib.pyplot as plt
import textwrap

# Tablodaki tüm veriyi liste formatında tanımlıyoruz
data = [
    ["Thank you for the detailed article, it really helped me understand the topic better.", "0.0933 (Güvenli)", "0.0057 (Güvenli)", "0.0074 (Güvenli)", "0.0014 (Güvenli)", "0.0020 (Güvenli)"],
    ["I disagree with your point of view, but I can see why you might think that way.", "0.2168 (Güvenli)", "0.0031 (Güvenli)", "0.0045 (Güvenli)", "0.0036 (Güvenli)", "0.0027 (Güvenli)"],
    ["Could you please clarify what you mean in the third paragraph?", "0.1471 (Güvenli)", "0.0043 (Güvenli)", "0.0040 (Güvenli)", "0.0017 (Güvenli)", "0.0021 (Güvenli)"],
    ["The weather is really nice today, I think I'll go for a walk.", "0.5212 (Dikkat)", "0.0160 (Güvenli)", "0.0136 (Güvenli)", "0.0027 (Güvenli)", "0.0036 (Güvenli)"],
    ["You are killing it with these new updates! Amazing job!", "0.4679 (Dikkat)", "0.0677 (Güvenli)", "0.0655 (Güvenli)", "0.6353 (Toksik)", "0.3291 (Dikkat)"],
    ["I'm not a racist, but people who live there are so lazy sometimes.", "0.7553 (Toksik)", "0.3907 (Dikkat)", "0.4002 (Dikkat)", "0.7508 (Toksik)", "0.6771 (Toksik)"],
    ["This movie is a complete garbage and a waste of time.", "0.6038 (Toksik)", "0.6074 (Toksik)", "0.5715 (Dikkat)", "0.8794 (Toksik)", "0.8798 (Toksik)"],
    ["You are a complete idiot, shut your mouth and never speak again.", "0.9947 (Toksik)", "0.9998 (Toksik)", "0.9998 (Toksik)", "0.9855 (Toksik)", "0.9970 (Toksik)"],
    ["Wow, you are so stupid that it physically hurts me to read your comments.", "0.9306 (Toksik)", "0.6695 (Toksik)", "0.5626 (Dikkat)", "0.9644 (Toksik)", "0.9933 (Toksik)"],
    ["Nobody cares about your pathetic opinion, loser.", "0.9745 (Toksik)", "0.9834 (Toksik)", "0.9772 (Toksik)", "0.9535 (Toksik)", "0.9839 (Toksik)"],
    ["You are such a hypocrite clown.", "0.6326 (Toksik)", "0.9807 (Toksik)", "0.9312 (Toksik)", "0.9607 (Toksik)", "0.9951 (Toksik)"],
    ["Go f**k yourself, you absolute piece of s**t.", "0.7724 (Toksik)", "0.6556 (Toksik)", "0.7438 (Toksik)", "0.9931 (Toksik)", "0.9983 (Toksik)"],
    ["Motherf****r, I can't believe how dumb your entire existence is.", "0.8333 (Toksik)", "0.6412 (Toksik)", "0.6607 (Toksik)", "0.9917 (Toksik)", "0.9937 (Toksik)"],
    ["Kiss my a$$, you annoying b**ch.", "0.4155 (Dikkat)", "0.4043 (Dikkat)", "0.4790 (Dikkat)", "0.9908 (Toksik)", "0.9974 (Toksik)"],
    ["All gay people should just be sent to prison, they are disgusting.", "0.9911 (Toksik)", "0.9092 (Toksik)", "0.9205 (Toksik)", "0.9419 (Toksik)", "0.9921 (Toksik)"],
    ["Black people are the reason this country is failing, pack your bags and leave.", "0.8444 (Toksik)", "0.3341 (Dikkat)", "0.5635 (Dikkat)", "0.8016 (Toksik)", "0.9606 (Toksik)"],
    ["Muslims are all terrorists and should be banned from entering.", "0.4388 (Dikkat)", "0.1862 (Güvenli)", "0.1981 (Güvenli)", "0.7952 (Toksik)", "0.9379 (Toksik)"],
    ["I know where you live and I am going to come to your house and kill you tonight.", "0.9955 (Toksik)", "0.7401 (Toksik)", "0.8453 (Toksik)", "0.7811 (Toksik)", "0.8721 (Toksik)"],
    ["I will slit your throat if you ever post something like this again.", "0.5045 (Dikkat)", "0.0819 (Güvenli)", "0.0368 (Güvenli)", "0.8423 (Toksik)", "0.8390 (Toksik)"],
    ["Somebody should shoot you in the head to make the world a better place.", "0.6794 (Toksik)", "0.1679 (Güvenli)", "0.2451 (Güvenli)", "0.7381 (Toksik)", "0.8268 (Toksik)"]
]

# Uzun yorumları tablo içinde tek satırda tutuyoruz (alt alta yazma kaldırıldı)
for i in range(len(data)):
    # Var olan yeni satır karakterlerini kaldır ve özel karakterleri kaçır
    data[i][0] = data[i][0].replace('\n', ' ').replace('$', '\\$')


columns = ["Yorum", "V1", "V2", "V2.1", "V3", "V4"]
df = pd.DataFrame(data, columns=columns)

# Resim boyutu ayarları — daha dar ve kompakt görünüm
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('off')
ax.axis('tight')

# Hesapla: en uzun yorumun piksel genişliğini ölç ve ilk sütunu ona göre ayarla
from matplotlib.font_manager import FontProperties
fp = FontProperties(size=11)

# Gerekli renderer'ı oluşturmak için figürü çiz
fig.canvas.draw()
renderer = fig.canvas.get_renderer()

max_pixel_width = 0
for row in data:
    txt = row[0]
    t = plt.text(0, 0, txt, fontproperties=fp)
    bb = t.get_window_extent(renderer=renderer)
    w = bb.width
    if w > max_pixel_width:
        max_pixel_width = w
    t.remove()

# Eksen genişliği (pixel)
axes_bb = ax.get_window_extent(renderer=renderer)
axes_width_px = axes_bb.width

# İlk sütun oranı: en uzun metin genişliği + 6px (3px her yandan)
first_col_frac = (max_pixel_width + 6) / axes_width_px if axes_width_px > 0 else 0.6
first_col_frac = min(max(first_col_frac, 0.05), 0.95)

# Biraz daha diğer sütunlara pay ver: ilk sütunu küçükçe azalt
extra_share = 0.12  # tüm eksende %12 civarı diğer sütunlara ek pay (daha fazla genişlik)
first_col_frac = max(first_col_frac - extra_share, 0.05)

# Diğer sütunlara eşit pay ver
n_other = len(columns) - 1
other_frac = (1.0 - first_col_frac) / n_other if n_other > 0 else (1.0 - first_col_frac)

table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
table.auto_set_font_size(False)
table.set_fontsize(11)

# Sütun genişlikleri ve arka plan renklendirmesi
# İlk sütun daha geniş (yorumlar için), diğer sütunlar dar ve eşit
for (row, col), cell in table.get_celld().items():
    if col == 0:
        cell.set_width(first_col_frac)
    else:
        cell.set_width(other_frac)

    # Satır yüksekliğini küçültüyoruz (daha basık görünüm)
    if row == 0:
        cell.set_height(0.06)
    else:
        cell.set_height(0.04)

    cell.set_edgecolor('#cccccc')

    # Başlık Satırı Tasarımı (Koyu Lacivert)
    if row == 0:
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(weight='bold', color='white', fontsize=12)
    else:
        text = cell.get_text().get_text()
        if col == 0: # Sadece Yorumun olduğu sütun
            # Metin özellikleri
            cell.set_text_props(fontsize=11)
            # Hücrenin dahili hizalaması ve padding'i doğrudan ayarlanıyor
            try:
                cell._loc = 'left'
                cell.PAD = 0.01  # gerekirse 0.0 yapabilirsiniz
            except Exception:
                # Bazı matplotlib sürümlerinde bu öznitelikler farklı olabilir; sessizce devam et
                pass
            cell.set_facecolor('#fdfdfd')
        else: # Skor sütunları (Koşullu Renklendirme)
            if "Güvenli" in text:
                cell.set_facecolor('#e8f5e9')
                cell.set_text_props(color='#2e7d32', weight='bold', fontsize=11)
            elif "Dikkat" in text:
                cell.set_facecolor('#fff8e1')
                cell.set_text_props(color='#f57f17', weight='bold', fontsize=11)
            elif "Toksik" in text:
                cell.set_facecolor('#ffebee')
                cell.set_text_props(color='#c62828', weight='bold', fontsize=11)

plt.title("ToxicGuard Versiyon Karşılaştırma Tablosu", fontsize=20, fontweight='bold', pad=15)
# Daha sıkı kenar boşlukları ile basık görünümü güçlendir
plt.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.02)

# Resmi bilgisayarına kaydeder
plt.savefig('toksisite_karsilastirma.png', dpi=300, bbox_inches='tight')
print("Görsel başarıyla oluşturuldu!")