#!/usr/bin/env python
# coding: utf-8

# In[ ]:


party_list = ['ak parti', 'iyi parti', 'sol parti', 'buyuk birlik', 'memleket',
             'anap', 'dsp', 'yeniden refah', 'dem parti', 'tkp',
             'abp', 'zafer partisi', 'hkp', 'tkh', 'btp',
             'gelecek partisi', 'ytp', 'chp', 'emep', 'huda par',
             'hak-par', 'ocak', 'ab parti', 'dp', 'gbp',
             'millet', 'milli yol', 'ap', 'gencparti', 'adp',
             'mhp', 'tip', 'deva partisi', 'saadet', 'vatan partisi', 'bagimsiz toplam oy']


color_map = {'ak parti': 'palegoldenrod', 'iyi parti': 'turquoise', 'sol parti': 'aqua', 'buyuk birlik': 'darkorange', 'memleket': 'lightblue',
             'anap': 'yellow', 'dsp': 'deeppink', 'yeniden refah': 'yellowgreen', 'dem parti': 'orchid', 'tkp': 'maroon',
             'abp': 'bisque', 'zafer partisi': 'saddlebrown', 'hkp': 'lightcoral', 'tkh': 'indianred', 'btp': 'chocolate',
             'gelecek': 'green', 'ytp': 'coral', 'chp': 'orangered', 'emep': 'firebrick', 'huda par': 'lawngreen',
             'hak-par': 'palegreen', 'ocak': 'sienna', 'ab parti': 'khaki', 'dp': 'brown', 'gbp': 'wheat',
             'millet': 'gold', 'milli yol': 'darkseagreen', 'ap': 'darkkhaki', 'gencparti': 'white', 'adp': 'rosybrown',
             'mhp': 'royalblue', 'tip': 'indigo', 'deva partisi': 'aquamarine', 'saadet': 'darkolivegreen', 'vatan partisi': 'magenta',
             'bagimsiz': 'lightsteelblue', 'diger': 'slategrey', 1.0: 'limegreen', 2.0: 'yellowgreen', 3.0: 'yellow', 4.0: 'orange', 5.0: 'red', 6.0: 'darkred',
             'ege': 'cyan', 'akdeniz': 'red', 'karadeniz': 'green', 'marmara': 'blue', 'güneydoğu anadolu': 'purple', 'iç anadolu': 'olive', 'doğu anadolu': 'brown'}

tooltip_texts = {
    'year_combo': 
    (
        "İncelenecek yerel seçim senesini seçiniz.\n"
        "Bu programda 2019 ve 2024 yerel seçimleri için veriler mevcuttur."
    ),
    'electiontype_combo': 
    (
        "İnceleme için kullanılacak oy türünü seçiniz.\n"
        "Yerel seçimlerde seçmenler belediye başkanı ve belediye meclisi için ayrı oy kullanır.\n"
        "Büyükşehirlerde ilçe başkanı, ilçe meclisi ve büyükşehir başkanı için oy kullanılır.\n"
        "İllerde ise ilçe başkanı, ilçe meclisi ve il meclisi için oy kullanılır.\n"
        "Seçim türü ile seçim seviyesinin kombinasyonu, incelenecek oyları belirler.\n"
        "   Örneğin; 2024 + başkanlık + ilçe = 2024 yerel seçimlerinde ilçe başkanlığı oylarını belirler."
    ),
    'level_combo': 
    (
        "İncelemenin yapılacağı idari bölge seviyesini seçiniz.\n"
        "Büyükşehirler için olası seçenekler 'büyükşehir' ve 'ilçe'dir.\n"
        "İller için olası seçenekler 'il' ve 'ilçe'dir.\n"
        "Belde verilerine de 'ilçe' seçilerek ulaşılır.\n"
        "Seçim türü ile seçim seviyesinin kombinasyonu, incelenecek oyları belirler.\n"
        "   Örneğin; 2019 + meclis + il = 2019 yerel seçimlerinde il meclisleri oylarını belirler."
    ),
    'analysis_combo': 
    (
        "Gerçekleştirilecek analiz tipini seçiniz.\n\n"
        "   Kategorik: Alt menülerde sağlanan kategori seçenekleri arasından kategori ve alt kategori seçilir.\n"
        "   Yapılan kategori seçimlerine göre gruplanan oyların partilere göre dağılımı üzerinden dairesel grafik üretilir.\n\n"
        "      Mevcut kategoriler:\n\n"
        "         SEGE: Sosyo-Ekonomik Gelişmişlik Sıralaması Araştırmaları, Sanayi ve Teknoloji Bakanlığı tarafından\n"
        "         gerçekleştirilen, illerin ve ilçelerin sosyo-ekonomik gelişmişliklerini nesnel olarak ölçen ve karşılaştıran analiz çalışmalarıdır.\n"
        "         En yüksek 1, en düşük 6 olacak şekilde 6 SEGE kademesi bulunmaktadır.\n"
        "         Daha fazla bilgi için: https://www.sanayi.gov.tr/merkez-birimi/b94224510b7b/sege adresine ulaşabilirsiniz.\n\n"
        "         Bölge: 6 Haziran-21 Haziran 1941 tarihleri arasında Ankara'da toplanan Birinci Coğrafya Kongresi tarafından belirlenen\n"
        "         coğrafi bölgeler. Türkiye İstatistiki Bölge Birimleri Sınıflandırması ile karıştırılmamalıdır.\n\n"
        "   Şehir: Alt menülerde sağlanan seçenekler ile il, ilçe ve belde seçilir.\n"
        "   Başkanlık oyları için illerde, meclis oyları için ise büyükşehirlerde 'ilçeler toplamı' seçeneği bulunmaktadır.\n\n"
        "   Parti: Alt menülerde sağlanan seçenekler ile belirlenen bir kategori dahilinde belirli bir partinin\n"
        "   aldığı toplam oyun bahsi geçen kategorinin alt kategorine göre dağılımını gösterir.\n"
        "      Örneğin; Ak Parti'nin belirlenen oy türü için elde ettiği toplam oyun, coğrafi bölgelere göre dağılımı.\n\n"
        "   Ülke geneli: Ülke genelinde verilerin partilere göre dağılımını gösterir.\n"
        "   Toplam oy dışında kazanılan belediye sayısı, salt çoğunluk elde edilen belediye meclisi sayısı gibi veriler bulunmaktadır."
        
    ),
    'threshold_entry': 
    (
        "'Diğer' kategorisinde toplanılacak partiler için yüzdelik olarak baraj sınırı belirtiniz.\n"
        "Belirtilen yüzdenin altına oy alan partiler, 'Diğer' kategorisine eklenir."
    )}

# Used to remove conflicting subcategory selections from category combo options.
groupby_remover = {'il': ' ilce ', 'ilçe': ' il ', 'büyükşehir': ' ilce '}

# A list of currently available category types, utilized for categorical ("kategorik") analysis.
groupby_list = ['SEGE il kademe', 'SEGE ilce kademe', 'bolge']

size_configurations = {
    "1920x1080": {
        "app_size": {"width": 1500, "height": 900},
        "frame_sizes": {
            "pie_chart_frame": {"width": 600, "height": 600},
            "data_table_frame": {"width": 1100, "height": 600},
            "data_frame": {"width": 150, "height": 600},
            "analysis_container_frame": {"width": 150, "height": 600},
            "chart_frame": {"width": 600, "height": 600},
            "analysis_frame": {"width": 600, "height": 400},
            "index_frame_min_width": 200,
            "tree_frame_min_width": 600
        },
        "widget_sizes": {
            "combobox_width": 15,
            "button_width": 12,
            "help_button_width": 2,
            "entry_width": 10,
            "text_area_width": 25
        },
        "tooltip_size": {"width": 800, "height": 400},
        "spacing": {"padx": 5, "pady": 5}
    },
    "1366x768": {
        "app_size": {"width": 1067, "height": 640},
        "frame_sizes": {
            "pie_chart_frame": {"width": 427, "height": 427},
            "data_table_frame": {"width": 783, "height": 427},
            "data_frame": {"width": 107, "height": 427},
            "analysis_container_frame": {"width": 107, "height": 427},
            "chart_frame": {"width": 427, "height": 427},
            "analysis_frame": {"width": 427, "height": 285},
            "index_frame_min_width": 142,
            "tree_frame_min_width": 427
        },
        "widget_sizes": {
            "combobox_width": 11,
            "button_width": 9,
            "help_button_width": 2,
            "entry_width": 7,
            "text_area_width": 19
        },
        "tooltip_size": {"width": 570, "height": 285},
        "spacing": {"padx": 5, "pady": 5}
    },
    "1440x900": {
        "app_size": {"width": 1125, "height": 750},
        "frame_sizes": {
            "pie_chart_frame": {"width": 450, "height": 500},
            "data_table_frame": {"width": 825, "height": 500},
            "data_frame": {"width": 113, "height": 500},
            "analysis_container_frame": {"width": 113, "height": 500},
            "chart_frame": {"width": 450, "height": 500},
            "analysis_frame": {"width": 450, "height": 333},
            "index_frame_min_width": 150,
            "tree_frame_min_width": 450
        },
        "widget_sizes": {
            "combobox_width": 12,
            "button_width": 10,
            "help_button_width": 2,
            "entry_width": 8,
            "text_area_width": 21
        },
        "tooltip_size": {"width": 600, "height": 300},
        "spacing": {"padx": 5, "pady": 5}
    },
    "1536x864": {
        "app_size": {"width": 1200, "height": 720},
        "frame_sizes": {
            "pie_chart_frame": {"width": 480, "height": 480},
            "data_table_frame": {"width": 880, "height": 480},
            "data_frame": {"width": 120, "height": 480},
            "analysis_container_frame": {"width": 120, "height": 480},
            "chart_frame": {"width": 480, "height": 480},
            "analysis_frame": {"width": 480, "height": 320},
            "index_frame_min_width": 160,
            "tree_frame_min_width": 480
        },
        "widget_sizes": {
            "combobox_width": 13,
            "button_width": 11,
            "help_button_width": 2,
            "entry_width": 9,
            "text_area_width": 22
        },
        "tooltip_size": {"width": 640, "height": 320},
        "spacing": {"padx": 5, "pady": 5}
    },
    "1600x900": {
        "app_size": {"width": 1250, "height": 750},
        "frame_sizes": {
            "pie_chart_frame": {"width": 500, "height": 500},
            "data_table_frame": {"width": 917, "height": 500},
            "data_frame": {"width": 125, "height": 500},
            "analysis_container_frame": {"width": 125, "height": 500},
            "chart_frame": {"width": 500, "height": 500},
            "analysis_frame": {"width": 500, "height": 333},
            "index_frame_min_width": 167,
            "tree_frame_min_width": 500
        },
        "widget_sizes": {
            "combobox_width": 13,
            "button_width": 11,
            "help_button_width": 2,
            "entry_width": 9,
            "text_area_width": 23
        },
        "tooltip_size": {"width": 667, "height": 333},
        "spacing": {"padx": 5, "pady": 5}
    },
    "2560x1440": {
        "app_size": {"width": 2000, "height": 1350},
        "frame_sizes": {
            "pie_chart_frame": {"width": 800, "height": 800},
            "data_table_frame": {"width": 1467, "height": 800},
            "data_frame": {"width": 200, "height": 800},
            "analysis_container_frame": {"width": 200, "height": 800},
            "chart_frame": {"width": 800, "height": 800},
            "analysis_frame": {"width": 800, "height": 533},
            "index_frame_min_width": 267,
            "tree_frame_min_width": 800
        },
        "widget_sizes": {
            "combobox_width": 20,
            "button_width": 16,
            "help_button_width": 2,
            "entry_width": 14,
            "text_area_width": 33
        },
        "tooltip_size": {"width": 1067, "height": 533},
        "spacing": {"padx": 5, "pady": 5}
    },
    "default": {
        "app_size": {"width": 1200, "height": 800},
        "frame_sizes": {
            "pie_chart_frame": {"width": 500, "height": 500},
            "data_table_frame": {"width": 900, "height": 500},
            "data_frame": {"width": 100, "height": 500},
            "analysis_container_frame": {"width": 100, "height": 500},
            "chart_frame": {"width": 500, "height": 500},
            "analysis_frame": {"width": 500, "height": 300},
            "index_frame_min_width": 150,
            "tree_frame_min_width": 500
        },
        "widget_sizes": {
            "combobox_width": 10,
            "button_width": 8,
            "help_button_width": 2,
            "entry_width": 8,
            "text_area_width": 20
        },
        "tooltip_size": {"width": 600, "height": 300},
        "spacing": {"padx": 5, "pady": 5}
    }
}