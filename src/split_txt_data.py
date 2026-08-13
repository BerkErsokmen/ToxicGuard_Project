import os
import math

def split_txt_file():
    input_file = 'data/test_yorumlari_sadece_metin.txt'
    output_dir = 'data/test_txt_parcalar'
    num_parts = 20
    
    if not os.path.exists(input_file):
        print(f"Hata: {input_file} bulunamadı.")
        return
        
    # Klasörü oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    # Tüm satırları oku
    print(f"Okunuyor: {input_file} ...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    total_lines = len(lines)
    lines_per_part = math.ceil(total_lines / num_parts)
    
    print(f"Toplam {total_lines} satır bulundu.")
    print(f"Her bir parça yaklaşık {lines_per_part} satır içerecek.")
    
    # Dosyaları böl ve yaz
    for i in range(num_parts):
        start_idx = i * lines_per_part
        end_idx = min((i + 1) * lines_per_part, total_lines)
        
        part_lines = lines[start_idx:end_idx]
        
        if not part_lines:
            break
            
        part_filename = f"test_yorumlari_parca_{i+1:02d}.txt"
        part_path = os.path.join(output_dir, part_filename)
        
        with open(part_path, 'w', encoding='utf-8') as out_f:
            out_f.writelines(part_lines)
            
    print(f"✅ İşlem tamamlandı. Dosyalar {output_dir}/ dizinine eklendi.")

if __name__ == "__main__":
    split_txt_file()
