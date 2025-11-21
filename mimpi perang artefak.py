import random
import json
import os
import time
from datetime import datetime

RAS_BONUS = {
    "Jawa": {"hp": 10, "mana": 5},
    "Sunda": {"speed": 2, "attack": 3},
    "Bali": {"mana": 8, "defense": 4},
    "Dayak": {"attack": 5, "durability": 3},
    "Bugis": {"luck": 4, "speed": 2}
}

RAS_UNLOCK_REQUIREMENTS = {
    "Sunda": "Kalahkan Guardian Hutan",
    "Bali": "Selesaikan Quest Seni", 
    "Dayak": "Kumpulkan 3 artefak Kalimantan",
    "Bugis": "Menang 10 pertempuran"
}

CLASS_BONUS = {
    "Fighter": {"hp": 20, "attack": 10, "defense": 5},
    "Assassin": {"speed": 15, "attack": 12, "luck": 8},
    "Archer": {"speed": 10, "attack": 8, "durability": 5},
    "Witch": {"mana": 30, "attack": 5, "defense": 3}
}

class Player:
    def __init__(self, name):
        self.name = name
        self.max_hp = 100
        self.current_hp = 100
        self.attack = 10
        self.defense = 5
        self.speed = 8
        self.durability = 6
        self.luck = 5
        self.mana = 50
        self.max_mana = 50
        self.equipped_artefaks = []
        self.inventory = []
        self.completed_quests = []
        self.current_location = "Desa Awal"
        self.game_time = "00:00:00"
        self.ras = "Jawa"
        self.unlocked_ras = ["Jawa"]
        self.battle_wins = 0
        self._cached_stats = None
        self.player_class = "Fighter"
        self.skills = self.get_class_skills()
        self.apply_ras_bonus()
        self.apply_class_bonus()
    
    def apply_ras_bonus(self):
        if self.ras in RAS_BONUS:
            bonuses = RAS_BONUS[self.ras]
            for stat, value in bonuses.items():
                if hasattr(self, stat):
                    current_value = getattr(self, stat)
                    setattr(self, stat, current_value + value)
    
    def apply_class_bonus(self):
        if self.player_class in CLASS_BONUS:
            bonuses = CLASS_BONUS[self.player_class]
            for stat, value in bonuses.items():
                if hasattr(self, stat):
                    current_value = getattr(self, stat)
                    setattr(self, stat, current_value + value)
    
    def get_class_skills(self):
        skills = {
            "Fighter": [
                {"name": "Heavy Strike", "mana_cost": 15, "damage_multiplier": 2.0, "description": "Serangan berat dengan damage 2x"},
                {"name": "Shield Bash", "mana_cost": 10, "damage_multiplier": 1.5, "description": "Serangan dengan perisai, mengurangi defense musuh"},
                {"name": "Battle Cry", "mana_cost": 20, "effect": "boost_attack", "description": "Meningkatkan attack untuk beberapa turn"}
            ],
            "Assassin": [
                {"name": "Backstab", "mana_cost": 20, "damage_multiplier": 2.5, "description": "Serangan dari belakang dengan damage tinggi"},
                {"name": "Poison Dart", "mana_cost": 15, "effect": "poison", "description": "Racun yang mengurangi HP musuh setiap turn"},
                {"name": "Shadow Step", "mana_cost": 25, "effect": "dodge", "description": "Menghindar dan mendapatkan serangan gratis"}
            ],
            "Archer": [
                {"name": "Precision Shot", "mana_cost": 12, "damage_multiplier": 1.8, "description": "Tembakan presisi dengan damage tinggi"},
                {"name": "Multi Shot", "mana_cost": 18, "damage_multiplier": 1.2, "hits": 3, "description": "Menembak beberapa anak panah sekaligus"},
                {"name": "Eagle Eye", "mana_cost": 15, "effect": "critical_boost", "description": "Meningkatkan chance critical hit"}
            ],
            "Witch": [
                {"name": "Fireball", "mana_cost": 25, "damage_multiplier": 2.2, "description": "Bola api dengan damage magic tinggi"},
                {"name": "Heal", "mana_cost": 20, "effect": "heal", "heal_amount": 30, "description": "Memulihkan HP"},
                {"name": "Mana Shield", "mana_cost": 15, "effect": "mana_shield", "description": "Membuat perisai dari mana"}
            ]
        }
        return skills.get(self.player_class, [])
    
    def change_class(self, new_class):
        if new_class in CLASS_BONUS:
            # Remove old class bonuses
            if self.player_class in CLASS_BONUS:
                old_bonuses = CLASS_BONUS[self.player_class]
                for stat, value in old_bonuses.items():
                    if hasattr(self, stat):
                        current_value = getattr(self, stat)
                        setattr(self, stat, current_value - value)
            # Apply new class
            self.player_class = new_class
            self.apply_class_bonus()
            self.skills = self.get_class_skills()
            self.invalidate_cache()
            return True
        return False
    
    def invalidate_cache(self):
        self._cached_stats = None
    
    def change_ras(self, new_ras):
        if new_ras in self.unlocked_ras:
            if self.ras in RAS_BONUS:
                old_bonuses = RAS_BONUS[self.ras]
                for stat, value in old_bonuses.items():
                    if hasattr(self, stat):
                        current_value = getattr(self, stat)
                        setattr(self, stat, current_value - value)
            self.ras = new_ras
            self.apply_ras_bonus()
            self.invalidate_cache()
            return True
        return False
    
    def unlock_ras(self, ras_name):
        if ras_name not in self.unlocked_ras and ras_name in RAS_UNLOCK_REQUIREMENTS:
            self.unlocked_ras.append(ras_name)
            print(f"Ras {ras_name} berhasil di-unlock!")
            return True
        return False
    
    def check_ras_unlocks(self):
        if "Guardian Hutan" in self.completed_quests:
            self.unlock_ras("Sunda")
        if "Quest Seni" in self.completed_quests:
            self.unlock_ras("Bali")
        kalimantan_artefaks = ["Mandau", "Perisai Talawang"]
        count = sum(1 for artefak in self.equipped_artefaks + self.inventory 
                   if artefak in kalimantan_artefaks)
        if count >= 3:
            self.unlock_ras("Dayak")
        if self.battle_wins >= 10:
            self.unlock_ras("Bugis")
    
    def equip_artefak(self, artefak):
        if len(self.equipped_artefaks) >= 7:
            return False
        if artefak in self.inventory:
            self.inventory.remove(artefak)
            self.equipped_artefaks.append(artefak)
            self.apply_artefak_effects(artefak)
            self.invalidate_cache()
            return True
        return False
    
    def unequip_artefak(self, artefak):
        if artefak in self.equipped_artefaks:
            self.equipped_artefaks.remove(artefak)
            self.inventory.append(artefak)
            self.remove_artefak_effects(artefak)
            self.invalidate_cache()
            return True
        return False
    
    def apply_artefak_effects(self, artefak):
        artefak_data = ARTEFAK_DATABASE[artefak]
        stats = artefak_data.get("stats", {})
        for stat, value in stats.items():
            if hasattr(self, stat):
                current_value = getattr(self, stat)
                setattr(self, stat, current_value + value)
    
    def remove_artefak_effects(self, artefak):
        artefak_data = ARTEFAK_DATABASE[artefak]
        stats = artefak_data.get("stats", {})
        for stat, value in stats.items():
            if hasattr(self, stat):
                current_value = getattr(self, stat)
                setattr(self, stat, current_value - value)
        self.current_hp = min(self.current_hp, self.max_hp)
        self.mana = min(self.mana, self.max_mana)
    
    def get_artefak_set_bonus(self):
        equipped_names = [artefak for artefak in self.equipped_artefaks]
        bonus_effects = {}
        if all(artefak in equipped_names for artefak in ["Kris", "Destar", "Baju Bodo"]):
            bonus_effects["Jawa_Complete"] = {"attack": 15, "mana": 10}
        if all(artefak in equipped_names for artefak in ["Mandau", "Perisai Talawang"]):
            bonus_effects["Kalimantan_Set"] = {"defense": 20, "hp": 25}
        return bonus_effects
    
    def get_total_stats(self):
        if self._cached_stats is None:
            stats = {
                'max_hp': self.max_hp,
                'attack': self.attack,
                'defense': self.defense,
                'speed': self.speed,
                'mana': self.mana
            }
            for artefak in self.equipped_artefaks:
                artefak_data = ARTEFAK_DATABASE.get(artefak, {})
                artefak_stats = artefak_data.get("stats", {})
                for stat, value in artefak_stats.items():
                    if stat in stats:
                        stats[stat] += value
            set_bonus = self.get_artefak_set_bonus()
            for bonus in set_bonus.values():
                for stat, value in bonus.items():
                    if stat in stats:
                        stats[stat] += value
            self._cached_stats = stats
        return self._cached_stats
    
    def display_stats(self):
        print(f"\n{'='*50}")
        print(f"PLAYER: {self.name} | CLASS: {self.player_class} | RAS: {self.ras}")
        print(f"HP: {self.current_hp}/{self.max_hp} | MANA: {self.mana}/{self.max_mana}")
        print(f"ATTACK: {self.attack} | DEFENSE: {self.defense} | SPEED: {self.speed}")
        print(f"LOCATION: {self.current_location} | WINS: {self.battle_wins}")
        print(f"{'='*50}")

class Enemy:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.max_hp = 50 + (level * 20)
        self.current_hp = self.max_hp
        self.attack = 5 + (level * 3)
        self.defense = 3 + (level * 2)
        self.speed = 4 + level
        self.artefak_drop = None
        self.drop_chance = 0.3
        self.effects = {}
    
    def display_stats(self):
        print(f"\n{'='*30}")
        print(f"MUSUH: {self.name} (Level {self.level})")
        print(f"HP: {self.current_hp}/{self.max_hp}")
        print(f"Attack: {self.attack} | Defense: {self.defense}")
        print(f"{'='*30}")

ARTEFAK_DATABASE = {
    "Tombak": {
        "type": "weapon",
        "rarity": "starter",
        "stats": {"attack": 5, "speed": 1},
        "effect": None,
        "description": "Tombak adalah senjata tradisional Jawa berupa lembing panjang. Dalam sejarah, tombak digunakan oleh para ksatria dan prajurit Kerajaan Majapahit sebagai senjata utama di medan perang.",
        "cultural_significance": "Tombak melambangkan kekuatan, keberanian, dan kewibawaan. Dalam budaya Jawa, tombak juga memiliki nilai spiritual dan sering digunakan dalam upacara adat."
    },
    "Perisai Talawang": {
        "type": "armor",
        "rarity": "starter", 
        "stats": {"defense": 8, "speed": -1},
        "effect": None,
        "description": "Talawang adalah perisai tradisional dari suku Dayak di Kalimantan. Terbuat dari kayu ulin yang kuat dan tahan lama, perisai ini memiliki ukiran khas dengan motif protektif.",
        "cultural_significance": "Dalam budaya Dayak, Talawang tidak hanya berfungsi sebagai pelindung fisik tetapi juga sebagai pelindung spiritual. Ukiran pada talawang dipercaya memiliki kekuatan magis untuk mengusir roh jahat."
    },
    "Destar": {
        "type": "helmet",
        "rarity": "starter",
        "stats": {"defense": 3, "hp": 10},
        "effect": None,
        "description": "Destar adalah ikat kepala tradisional Jawa yang juga dikenal sebagai blangkon. Terbuat dari kain yang dilipat dengan rapi, destar menjadi simbol identitas budaya Jawa.",
        "cultural_significance": "Dalam masyarakat Jawa, destar atau blangkon melambangkan kesempurnaan, kesopanan, dan kematangan berpikir. Setiap lipatan pada destar memiliki makna filosofis tersendiri."
    },
    "Clurit": {
        "type": "weapon",
        "rarity": "common",
        "stats": {"attack": 8, "speed": 2},
        "effect": None,
        "description": "Clurit adalah senjata khas Madura berbentuk sabit dengan mata pisau melengkung. Senjata ini awalnya digunakan sebagai alat pertanian sebelum dimanfaatkan untuk pertahanan diri.",
        "cultural_significance": "Bagi masyarakat Madura, clurit bukan sekadar senjata tetapi simbol harga diri dan kehormatan. Dalam tradisi Karapan Sapi, clurit juga digunakan oleh para joki."
    },
    "Celuk": {
        "type": "accessory",
        "rarity": "common",
        "stats": {"luck": 3, "durability": 2},
        "effect": None,
        "description": "Celuk adalah cincin atau gelang tradisional Bali yang terbuat dari logam mulia. Celuk sering dihiasi dengan ukiran rumit dan batu permata.",
        "cultural_significance": "Dalam budaya Bali, celuk dipercaya memiliki kekuatan spiritual untuk melindungi pemakainya dari pengaruh negatif. Celuk juga menunjukkan status sosial dan kemakmuran pemakainya."
    },
    "Bokor": {
        "type": "accessory", 
        "rarity": "common",
        "stats": {"mana": 10, "defense": 2},
        "effect": None,
        "description": "Bokor adalah wadah atau mangkuk tradisional yang digunakan dalam upacara adat di berbagai daerah Indonesia. Terbuat dari logam atau kayu dengan ukiran indah.",
        "cultural_significance": "Bokor memiliki peran penting dalam ritual keagamaan dan upacara adat. Dalam budaya Jawa dan Bali, bokor sering digunakan sebagai tempat sesajen untuk para leluhur dan dewa-dewi."
    },
    "Rencong": {
        "type": "weapon",
        "rarity": "uncommon",
        "stats": {"attack": 12, "speed": 3},
        "effect": {
            "condition": "first_attack",
            "trigger": "battle_start",
            "damage": "bonus_5"
        },
        "description": "Rencong adalah senjata tradisional Aceh berbentuk pisau lengkung. Sebagai simbol kebanggaan Aceh, rencong selalu dibawa oleh pria Aceh sebagai bagian dari pakaian adat.",
        "cultural_significance": "Rencong memiliki makna mendalam dalam budaya Aceh. Bentuknya yang melengkung melambangkan sifat manusia yang rendah hati, sementara ujungnya yang tajam menggambarkan ketajaman pikiran dan keadilan."
    },
    "Baju Bodo": {
        "type": "armor",
        "rarity": "uncommon",
        "stats": {"defense": 12, "hp": 15},
        "effect": None,
        "description": "Baju Bodo adalah pakaian tradisional wanita Bugis-Makassar dari Sulawesi Selatan. Dibuat dari kain katun dengan warna-warna cerah, baju ini memiliki potongan yang khas dan longgar.",
        "cultural_significance": "Baju Bodo mencerminkan filosofi \"Sipakatau\" (saling menghargai) dan \"Sipakalebbi\" (saling menghormati) dalam masyarakat Bugis. Setiap warna pada baju bodo memiliki makna tersendiri sesuai status sosial pemakainya."
    },
    "Badong": {
        "type": "accessory",
        "rarity": "uncommon", 
        "stats": {"luck": 5, "mana": 8},
        "effect": None,
        "description": "Badong adalah gelang tradisional Toraja yang terbuat dari gading gajah atau tanduk kerbau. Gelang ini biasanya dipakai berpasangan di kedua tangan.",
        "cultural_significance": "Dalam budaya Toraja, badong merupakan simbol status sosial dan kemakmuran. Semakin banyak badong yang dipakai, semakin terhormat pemiliknya. Badong juga diyakini memiliki kekuatan magis untuk melindungi pemakainya."
    },
    "Trisula": {
        "type": "weapon",
        "rarity": "rare",
        "stats": {"attack": 18, "speed": 1},
        "effect": {
            "condition": "enemy_hp_above_50",
            "trigger": "attack",
            "damage": "extra_10_percent"
        },
        "description": "Trisula adalah senjata mistis berbentuk tombak bercabang tiga yang berasal dari kepercayaan Hindu-Buddha di Indonesia. Trisula sering dikaitkan dengan dewa Siwa dalam mitologi Hindu.",
        "cultural_significance": "Trisula melambangkan keseimbangan tiga kekuatan alam semesta: penciptaan, pemeliharaan, dan pemusnahan. Dalam budaya Jawa, trisula juga menjadi simbol kekuatan spiritual dan sering digunakan dalam ritual pertapaan."
    },
    "Kawaca": {
        "type": "armor",
        "rarity": "rare",
        "stats": {"defense": 15, "hp": 20, "durability": 5},
        "effect": None,
        "description": "Kawaca atau kawaca diri adalah baju besi tradisional Jawa yang terbuat dari logam atau kulit. Baju besi ini dirancang untuk melindungi tubuh pemakainya dengan tetap menjaga mobilitas.",
        "cultural_significance": "Dalam sejarah Jawa, kawaca sering dipakai oleh para raja dan ksatria. Baju besi ini tidak hanya melindungi secara fisik tetapi juga dipercaya memiliki kekuatan gaib (ajian) yang melindungi pemakainya dari senjata tajam."
    },
    "Keramon": {
        "type": "accessory",
        "rarity": "rare",
        "stats": {"speed": 4, "attack": 5},
        "effect": {
            "condition": "always",
            "trigger": "battle_start", 
            "effect": "first_strike"
        },
        "description": "Keramon adalah jimat atau rajah tradisional Jawa berbentuk kotak kecil yang berisi mantra dan simbol mistis. Keramon biasanya terbuat dari kayu, logam, atau tulang.",
        "cultural_significance": "Bagi masyarakat Jawa, keramon dipercaya memiliki kekuatan supranatural untuk melindungi pemakainya, memberikan keberanian, dan membawa keberuntungan. Keramon sering diberikan oleh seorang guru spiritual kepada muridnya setelah menjalani ritual tertentu."
    },
    "Kris": {
        "type": "weapon",
        "rarity": "epic",
        "stats": {"attack": 25, "speed": -3, "luck": 5},
        "effect": {
            "condition": "enemy_hp_full", 
            "trigger": "first_attack",
            "damage": "25_percent_max_hp"
        },
        "description": "Kris adalah senjata tradisional Indonesia berbentuk pisau asymetris dengan bilah berkelok-kelok. Merupakan warisan budaya dunia UNESCO, kris memiliki nilai seni dan spiritual yang sangat tinggi.",
        "cultural_significance": "Dalam budaya Jawa, kris bukan sekadar senjata tetapi simbol jiwa dan kekuatan spiritual. Setiap lekukan pada bilah kris memiliki makna filosofis. Kris juga dianggap sebagai pusaka yang memiliki kekuatan gaib (tuah) dan sering diwariskan secara turun-temurun."
    },
    "Mandau": {
        "type": "weapon",
        "rarity": "epic", 
        "stats": {"attack": 22, "speed": 2, "durability": 3},
        "effect": {
            "condition": "player_hp_below_30",
            "trigger": "attack",
            "damage": "double_damage"
        },
        "description": "Mandau adalah senjata tradisional suku Dayak di Kalimantan berupa pedang panjang dengan bilah lebar. Mandau memiliki ukiran khas dan hiasan dari bulu burung enggang.",
        "cultural_significance": "Bagi suku Dayak, mandau adalah simbol identitas, keberanian, dan kehormatan. Dalam tradisi Dayak, setiap mandau memiliki nama tersendiri dan dipercaya memiliki roh penjaga. Mandau juga digunakan dalam ritual kepala (Ngayau) dalam sejarah masa lalu."
    },
    "Siger": {
        "type": "helmet",
        "rarity": "epic",
        "stats": {"defense": 10, "hp": 25, "mana": 15},
        "effect": {
            "condition": "always",
            "trigger": "passive",
            "effect": "royal_aura"
        },
        "description": "Siger adalah mahkota tradisional Lampung berbentuk segitiga dengan hiasan bunga melati dan mutiara. Siger terbuat dari kuningan dengan ukiran rumit yang sangat artistik.",
        "cultural_significance": "Dalam budaya Lampung, siger merupakan simbol kemuliaan, kebanggaan, dan keagungan adat. Hanya wanita yang telah menikah dan berasal dari keluarga terhormat yang boleh memakai siger lengkap. Siger juga menjadi simbol persatuan sembilan marga di Lampung."
    },
    "Gamelan Mini": {
        "type": "accessory",
        "rarity": "rare",
        "stats": {"mana": 15, "luck": 3},
        "effect": {
            "condition": "always",
            "trigger": "passive", 
            "effect": "rhythm_bonus"
        },
        "description": "Gamelan adalah instrumen musik tradisional Jawa dan Bali yang terdiri dari metalofon, gong, kendang, dan rebab. Gamelan mini adalah versi kecil yang bisa dibawa sebagai jimat.",
        "cultural_significance": "Dalam budaya Jawa dan Bali, gamelan bukan sekadar alat musik tetapi memiliki fungsi sakral dalam upacara keagamaan dan ritual adat. Setiap nada dalam gamelan dipercaya memiliki kekuatan spiritual untuk menghubungkan manusia dengan alam semesta. Gamelan juga menjadi identitas budaya yang diakui UNESCO sebagai Warisan Budaya Takbenda Dunia."
    }
}

def penalty_minigame():
    print("\nMINI-GAME: PENALTY SHOOTOUT (Best of 3)")
    arah = ["kiri", "tengah", "kanan"]
    arah_tampil = ["Kiri", "Tengah", "Kanan"]
    player_wins = 0
    computer_wins = 0
    
    for round in range(1, 4):
        print(f"\n{'='*40}")
        print(f"RONDE {round}")
        print(f"{'='*40}")
        print("Pilih arah tendangan:")
        print("1. Kiri")
        print("2. Tengah") 
        print("3. Kanan")
        
        try:
            pilihan_player = int(input("Pilihanmu (1-3): ")) - 1
            if pilihan_player not in [0, 1, 2]:
                print("Pilihan tidak valid! Ronde dianggap kalah.")
                computer_wins += 1
                continue
        except ValueError:
            print("Masukkan angka 1-3! Ronde dianggap kalah.")
            computer_wins += 1
            continue
        
        pilihan_kiper = random.randint(0, 2)
        print(f"Kamu menendang ke {arah_tampil[pilihan_player]}!")
        print(f"Kiper melompat ke {arah_tampil[pilihan_kiper]}!")
        
        if pilihan_player == pilihan_kiper:
            print("DITAHAN! Kiper menyelamatkan tendanganmu!")
            computer_wins += 1
        else:
            print("GOOOOL! Tendanganmu masuk!")
            player_wins += 1
        
        print(f"\nSkor: Kamu {player_wins} - {computer_wins} Musuh")
        
        if player_wins == 2 or computer_wins == 2:
            break
    
    print(f"\n{'='*40}")
    print("HASIL AKHIR")
    print(f"{'='*40}")
    print(f"Skor: Kamu {player_wins} - {computer_wins} Musuh")
    return player_wins > computer_wins

def rock_paper_scissors():
    print("\nMINI-GAME: BATU KERTAS GUNTING (Best of 3)")
    choices = ["batu", "kertas", "gunting"]
    choices_tampil = ["Batu", "Kertas", "Gunting"]
    player_wins = 0
    computer_wins = 0
    
    for round in range(1, 4):
        print(f"\n{'='*40}")
        print(f"RONDE {round}")
        print(f"{'='*40}")
        print("Pilih tanganmu:")
        print("1. Batu")
        print("2. Kertas")
        print("3. Gunting")
        
        try:
            choice_num = int(input("Pilihanmu (1-3): "))
            if choice_num not in [1, 2, 3]:
                print("Pilihan tidak valid! Ronde dianggap kalah.")
                computer_wins += 1
                continue
            player_choice = choices[choice_num - 1]
            player_choice_tampil = choices_tampil[choice_num - 1]
        except ValueError:
            print("Masukkan angka 1-3! Ronde dianggap kalah.")
            computer_wins += 1
            continue
        
        computer_choice_idx = random.randint(0, 2)
        computer_choice = choices[computer_choice_idx]
        computer_choice_tampil = choices_tampil[computer_choice_idx]
        
        print(f"Kamu memilih: {player_choice_tampil}")
        print(f"Musuh memilih: {computer_choice_tampil}")
        
        if player_choice == computer_choice:
            print("SERI! Tidak ada poin.")
        elif (
            (player_choice == "batu" and computer_choice == "gunting") or
            (player_choice == "kertas" and computer_choice == "batu") or
            (player_choice == "gunting" and computer_choice == "kertas")
        ):
            print(f"{player_choice_tampil} mengalahkan {computer_choice_tampil}!")
            print("Kamu menang ronde ini!")
            player_wins += 1
        else:
            print(f"{computer_choice_tampil} mengalahkan {player_choice_tampil}!")
            print("Musuh menang ronde ini!")
            computer_wins += 1
        
        print(f"\nSkor: Kamu {player_wins} - {computer_wins} Musuh")
        
        if player_wins == 2 or computer_wins == 2:
            break
    
    print(f"\n{'='*40}")
    print("HASIL AKHIR")
    print(f"{'='*40}")
    print(f"Skor: Kamu {player_wins} - {computer_wins} Musuh")
    return player_wins > computer_wins

def elephant_human_ant():
    print("\nMINI-GAME: GAJAH MANUSIA SEMUT (Best of 3)")
    choices = ["gajah", "manusia", "semut"]
    choices_tampil = ["Gajah", "Manusia", "Semut"]
    rules = {
        "gajah": "manusia",  # Gajah mengalahkan manusia
        "manusia": "semut",  # Manusia mengalahkan semut
        "semut": "gajah"    # Semut mengalahkan gajah
    }
    player_wins = 0
    computer_wins = 0
    
    for round in range(1, 4):
        print(f"\n{'='*40}")
        print(f"RONDE {round}")
        print(f"{'='*40}")
        print("Pilih langkahmu:")
        print("1. Gajah")
        print("2. Manusia") 
        print("3. Semut")
        
        try:
            choice_num = int(input("Pilihanmu (1-3): "))
            if choice_num not in [1, 2, 3]:
                print("Pilihan tidak valid! Ronde dianggap kalah.")
                computer_wins += 1
                continue
            player_choice = choices[choice_num - 1]
            player_choice_tampil = choices_tampil[choice_num - 1]
        except ValueError:
            print("Masukkan angka 1-3! Ronde dianggap kalah.")
            computer_wins += 1
            continue
        
        computer_choice_idx = random.randint(0, 2)
        computer_choice = choices[computer_choice_idx]
        computer_choice_tampil = choices_tampil[computer_choice_idx]
        
        print(f"Kamu memilih: {player_choice_tampil}")
        print(f"Musuh memilih: {computer_choice_tampil}")
        
        if player_choice == computer_choice:
            print("SERI! Tidak ada poin.")
        elif rules[player_choice] == computer_choice:
            print(f"{player_choice_tampil} mengalahkan {computer_choice_tampil}!")
            print("Kamu menang ronde ini!")
            player_wins += 1
        else:
            print(f"{computer_choice_tampil} mengalahkan {player_choice_tampil}!")
            print("Musuh menang ronde ini!")
            computer_wins += 1
        
        print(f"\nSkor: Kamu {player_wins} - {computer_wins} Musuh")
        
        if player_wins == 2 or computer_wins == 2:
            break
    
    print(f"\n{'='*40}")
    print("HASIL AKHIR")
    print(f"{'='*40}")
    print(f"Skor: Kamu {player_wins} - {computer_wins} Musuh")
    return player_wins > computer_wins

def guess_number():
    print("\nMINI-GAME: TEBAK ANGKA (Best of 3)")
    player_wins = 0
    computer_wins = 0
    
    for round in range(1, 4):
        print(f"\n{'='*40}")
        print(f"RONDE {round}")
        print(f"{'='*40}")
        target = random.randint(1, 100)
        attempts = 5
        print(f"Tebak angka 1-100! Kamu punya {attempts} kesempatan.")
        guessed = False
        
        for attempt in range(attempts):
            try:
                guess = int(input(f"Tebakan {attempt + 1}: "))
                if guess == target:
                    print("TEPAT SEKALI! Kamu menebak dengan benar!")
                    player_wins += 1
                    guessed = True
                    break
                elif guess < target:
                    print("Terlalu RENDAH!")
                else:
                    print("Terlalu TINGGI!")
            except ValueError:
                print("Masukkan angka yang valid!")
        
        if not guessed:
            print(f"Gagal! Angka yang benar adalah {target}.")
            computer_wins += 1
        
        print(f"\nSkor: Kamu {player_wins} - {computer_wins} Musuh")
        
        if player_wins == 2 or computer_wins == 2:
            break
    
    print(f"\n{'='*40}")
    print("HASIL AKHIR")
    print(f"{'='*40}")
    print(f"Skor: Kamu {player_wins} - {computer_wins} Musuh")
    return player_wins > computer_wins

def math_quiz():
    print("\nMINI-GAME: SOAL MATEMATIKA (Best of 3)")
    operations = ['+', '-', '*', '/']
    player_wins = 0
    computer_wins = 0
    
    for round in range(1, 4):
        print(f"\n{'='*40}")
        print(f"RONDE {round}")
        print(f"{'='*40}")
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        operation = random.choice(operations)
        
        if operation == '+':
            correct_answer = num1 + num2
        elif operation == '-':
            correct_answer = num1 - num2
        elif operation == '*':
            correct_answer = num1 * num2
        else:
            num1 = num1 * num2
            correct_answer = num1 // num2
        
        try:
            user_answer = int(input(f"Soal: {num1} {operation} {num2} = "))
            if user_answer == correct_answer:
                print("BENAR! Kamu menang ronde ini!")
                player_wins += 1
            else:
                print(f"SALAH! Jawabannya: {correct_answer}")
                computer_wins += 1
        except ValueError:
            print("Masukkan angka yang valid! Ronde dianggap kalah.")
            computer_wins += 1
        
        print(f"\nSkor: Kamu {player_wins} - {computer_wins} Musuh")
        
        if player_wins == 2 or computer_wins == 2:
            break
    
    print(f"\n{'='*40}")
    print("HASIL AKHIR")
    print(f"{'='*40}")
    print(f"Skor: Kamu {player_wins} - {computer_wins} Musuh")
    return player_wins > computer_wins

def hide_and_seek():
    print("\nMINI-GAME: PETAK UMPET (Best of 3)")
    player_wins = 0
    computer_wins = 0
    
    for round in range(1, 4):
        print(f"\n{'='*40}")
        print(f"RONDE {round}")
        print(f"{'='*40}")
        print("Pilih tempat bersembunyi:")
        print("1. Belakang pohon")
        print("2. Dalam gua") 
        print("3. Atas gedung")
        
        try:
            player_hiding_spot = int(input("Pilihanmu (1-3): "))
            if player_hiding_spot not in [1, 2, 3]:
                print("Pilihan tidak valid! Ronde dianggap kalah.")
                computer_wins += 1
                continue
        except ValueError:
            print("Masukkan angka 1, 2, atau 3! Ronde dianggap kalah.")
            computer_wins += 1
            continue
        
        spot_names = {1: "Belakang pohon", 2: "Dalam gua", 3: "Atas gedung"}
        print(f"Kamu bersembunyi di: {spot_names[player_hiding_spot]}")
        
        search_spots = random.sample([1, 2, 3], 2)
        searched_spots = [spot_names[spot] for spot in search_spots]
        print(f"Musuh mencari di: {', '.join(searched_spots)}")
        
        if player_hiding_spot in search_spots:
            print("KAMU DITEMUKAN! Kalah ronde ini.")
            computer_wins += 1
        else:
            print("AMAN! Kamu tidak ditemukan. Menang ronde ini!")
            player_wins += 1
        
        print(f"\nSkor: Kamu {player_wins} - {computer_wins} Musuh")
        
        if player_wins == 2 or computer_wins == 2:
            break
    
    print(f"\n{'='*40}")
    print("HASIL AKHIR")
    print(f"{'='*40}")
    print(f"Skor: Kamu {player_wins} - {computer_wins} Musuh")
    return player_wins > computer_wins

def rhythm_minigame():
    print("\nMINI-GAME: RHYTHM OF BATTLE (Best of 3)")
    sequence = ["←", "↑", "→", "↓"]
    sequence_names = {"←": "Kiri", "↑": "Atas", "→": "Kanan", "↓": "Bawah"}
    player_wins = 0
    computer_wins = 0
    
    for round in range(1, 4):
        print(f"\n{'='*40}")
        print(f"RONDE {round}")
        print(f"{'='*40}")
        target_sequence = random.sample(sequence, 3)
        print("Hafalkan urutan gerakan:")
        print(" ".join([sequence_names[move] for move in target_sequence]))
        time.sleep(2)
        print("\n" * 10)
        
        print("Sekarang ulangi gerakan:")
        player_sequence = []
        for i in range(3):
            print(f"Gerakan {i+1}:")
            print("1. Kiri (←)")
            print("2. Atas (↑)")
            print("3. Kanan (→)")
            print("4. Bawah (↓)")
            try:
                move_choice = int(input("Pilihan (1-4): "))
                if move_choice == 1:
                    player_sequence.append("←")
                elif move_choice == 2:
                    player_sequence.append("↑")
                elif move_choice == 3:
                    player_sequence.append("→")
                elif move_choice == 4:
                    player_sequence.append("↓")
                else:
                    print("Pilihan tidak valid! Dianggap salah.")
                    player_sequence.append("X")
            except ValueError:
                print("Masukkan angka 1-4! Dianggap salah.")
                player_sequence.append("X")
        
        print(f"\nUrutan kamu: {' '.join([sequence_names.get(move, 'Salah') for move in player_sequence])}")
        print(f"Urutan benar: {' '.join([sequence_names[move] for move in target_sequence])}")
        
        if player_sequence == target_sequence:
            print("URUTAN BENAR! Menang ronde ini!")
            player_wins += 1
        else:
            print("URUTAN SALAH! Kalah ronde ini!")
            computer_wins += 1
        
        print(f"\nSkor: Kamu {player_wins} - {computer_wins} Musuh")
        
        if player_wins == 2 or computer_wins == 2:
            break
    
    print(f"\n{'='*40}")
    print("HASIL AKHIR")
    print(f"{'='*40}")
    print(f"Skor: Kamu {player_wins} - {computer_wins} Musuh")
    return player_wins > computer_wins

MINI_GAMES = {
    "penalty": penalty_minigame,
    "rhythm": rhythm_minigame,
    "rock_paper_scissors": rock_paper_scissors,
    "elephant_human_ant": elephant_human_ant,
    "guess_number": guess_number,
    "math_quiz": math_quiz,
    "hide_and_seek": hide_and_seek
}

def trigger_random_minigame(reward_type):
    game_name, game_func = random.choice(list(MINI_GAMES.items()))
    game_title = game_name.replace('_', ' ').upper()
    
    print(f"\n{'='*50}")
    print(f"MINI-GAME: {game_title} (Best of 3)")
    print(f"REWARD: {reward_type}")
    print(f"{'='*50}")
    
    success = game_func()
    
    if success:
        print(f"\n{'='*50}")
        print("KAMU MENANG MINI-GAME!")
        print(f"Mendapatkan {reward_type}!")
        print(f"{'='*50}")
        return True
    else:
        print(f"\n{'='*50}")
        print("KAMU KALAH MINI-GAME!")
        print(f"Tidak mendapatkan {reward_type}.")
        print(f"{'='*50}")
        return False

def battle_system(player, enemy):
    try:
        if player.current_hp <= 0:
            print("Player HP sudah habis, tidak bisa bertarung!")
            return False
        
        print(f"\nPERTEMPURAN MELAWAN {enemy.name}!")
        enemy.display_stats()
        
        battle_ongoing = True
        player_turn = player.speed >= enemy.speed
        special_effects = {
            "double_damage": False,
            "first_strike": False,
            "boost_attack": 0,
            "poison": 0,
            "dodge": False,
            "critical_boost": 0,
            "mana_shield": False
        }
        
        for artefak in player.equipped_artefaks:
            artefak_data = ARTEFAK_DATABASE[artefak]
            effect = artefak_data.get("effect")
            if effect and effect["trigger"] == "battle_start":
                if effect.get("effect") == "first_strike":
                    player_turn = True
                    special_effects["first_strike"] = True
                    print("Efek artefak memberimu first strike!")
        
        while battle_ongoing:
            if player_turn:
                print(f"\n{'='*30}")
                print(f"GILIRAN {player.name}")
                print(f"{'='*30}")
                print("1. Serang Basic")
                print("2. Gunakan Skill Class")
                print("3. Gunakan Efek Artefak") 
                print("4. Bertahan")
                print("5. Kabur")
                print("6. Lihat Inventory")
                
                try:
                    choice = int(input("Pilihan (1-6): "))
                    if choice == 1:
                        damage = max(1, player.attack - enemy.defense // 2)
                        if special_effects["double_damage"]:
                            damage *= 2
                            special_effects["double_damage"] = False
                        if special_effects["boost_attack"] > 0:
                            damage = int(damage * 1.5)
                            special_effects["boost_attack"] -= 1
                        enemy.current_hp -= damage
                        print(f"Kamu menyerang {enemy.name} dan menyebabkan {damage} damage!")
                        
                        if enemy.current_hp <= 0:
                            print(f"{enemy.name} dikalahkan!")
                            player.battle_wins += 1
                            player.check_ras_unlocks()
                            battle_ongoing = False
                            return True
                    elif choice == 2:
                        player.display_skills()
                        try:
                            skill_choice = int(input("Pilih skill (angka): ")) - 1
                            if 0 <= skill_choice < len(player.skills):
                                skill = player.skills[skill_choice]
                                mana_cost = skill.get('mana_cost', 0)
                                if player.mana >= mana_cost:
                                    player.mana -= mana_cost
                                    print(f"Menggunakan {skill['name']}!")
                                    
                                    if 'damage_multiplier' in skill:
                                        damage = max(1, int(player.attack * skill['damage_multiplier']) - enemy.defense // 2)
                                        enemy.current_hp -= damage
                                        print(f"Skill menyebabkan {damage} damage!")
                                        
                                        if 'hits' in skill:
                                            for i in range(skill['hits'] - 1):
                                                extra_damage = max(1, int(player.attack * skill['damage_multiplier'] * 0.8) - enemy.defense // 2)
                                                enemy.current_hp -= extra_damage
                                                print(f"Hit tambahan: {extra_damage} damage!")
                                    
                                    if 'effect' in skill:
                                        effect = skill['effect']
                                        if effect == 'heal':
                                            heal_amount = skill.get('heal_amount', 30)
                                            player.current_hp = min(player.max_hp, player.current_hp + heal_amount)
                                            print(f"Memulihkan {heal_amount} HP!")
                                        elif effect == 'boost_attack':
                                            special_effects["boost_attack"] = 3
                                            print("Attack meningkat untuk 3 turn!")
                                        elif effect == 'poison':
                                            enemy.effects['poison'] = 3
                                            print("Musuh terkena racun!")
                                        elif effect == 'dodge':
                                            special_effects["dodge"] = True
                                            print("Kamu siap menghindar!")
                                        elif effect == 'critical_boost':
                                            special_effects["critical_boost"] = 2
                                            print("Chance critical hit meningkat!")
                                        elif effect == 'mana_shield':
                                            special_effects["mana_shield"] = True
                                            print("Perisai mana aktif!")
                                    
                                    if enemy.current_hp <= 0:
                                        print(f"{enemy.name} dikalahkan!")
                                        player.battle_wins += 1
                                        player.check_ras_unlocks()
                                        battle_ongoing = False
                                        return True
                                else:
                                    print("Mana tidak cukup!")
                                    continue
                            else:
                                print("Pilihan skill tidak valid!")
                                continue
                        except (ValueError, IndexError):
                            print("Pilihan tidak valid!")
                            continue
                    elif choice == 3:
                        usable_artefaks = []
                        for artefak in player.equipped_artefaks:
                            artefak_data = ARTEFAK_DATABASE[artefak]
                            if artefak_data.get("effect") and artefak_data["effect"]["trigger"] == "attack":
                                usable_artefaks.append(artefak)
                        
                        if not usable_artefaks:
                            print("Tidak ada artefak dengan efek yang bisa digunakan!")
                            continue
                        
                        print("Pilih artefak untuk aktivasi efek:")
                        for i, artefak in enumerate(usable_artefaks, 1):
                            print(f"{i}. {artefak}")
                        
                        try:
                            artefak_choice = int(input("Pilihan: ")) - 1
                            selected_artefak = usable_artefaks[artefak_choice]
                            artefak_data = ARTEFAK_DATABASE[selected_artefak]
                            effect = artefak_data["effect"]
                            condition_met = False
                            
                            if effect["condition"] == "enemy_hp_above_50":
                                condition_met = enemy.current_hp > enemy.max_hp * 0.5
                            elif effect["condition"] == "player_hp_below_30":
                                condition_met = player.current_hp < player.max_hp * 0.3
                            elif effect["condition"] == "always":
                                condition_met = True
                            
                            if condition_met:
                                if effect["damage"] == "extra_10_percent":
                                    bonus_damage = int(enemy.max_hp * 0.1)
                                    enemy.current_hp -= bonus_damage
                                    print(f"Efek {selected_artefak} aktif! Bonus {bonus_damage} damage!")
                                elif effect["damage"] == "double_damage":
                                    special_effects["double_damage"] = True
                                    print(f"Efek {selected_artefak} aktif! Serangan berikutnya double damage!")
                                elif effect["damage"] == "bonus_5":
                                    bonus_damage = 5
                                    enemy.current_hp -= bonus_damage
                                    print(f"Efek {selected_artefak} aktif! Bonus {bonus_damage} damage!")
                                elif effect["damage"] == "25_percent_max_hp":
                                    damage = int(enemy.max_hp * 0.25)
                                    enemy.current_hp -= damage
                                    print(f"Efek {selected_artefak} aktif! Damage {damage}!")
                                
                                if enemy.current_hp <= 0:
                                    print(f"{enemy.name} dikalahkan!")
                                    player.battle_wins += 1
                                    player.check_ras_unlocks()
                                    battle_ongoing = False
                                    return True
                            else:
                                print(f"Kondisi untuk efek {selected_artefak} tidak terpenuhi!")
                                continue
                        except (ValueError, IndexError):
                            print("Pilihan tidak valid!")
                            continue
                    elif choice == 4:
                        print("Kamu bertahan, defense meningkat untuk giliran ini!")
                        player.defense += 5
                        special_effects["dodge"] = True
                    elif choice == 5:
                        flee_chance = player.speed / (player.speed + enemy.speed) * 0.5 + player.luck * 0.01
                        if random.random() < flee_chance:
                            print("Berhasil kabur dari pertempuran!")
                            return False
                        else:
                            print("Gagal kabur!")
                    elif choice == 6:
                        display_inventory(player)
                        continue
                    else:
                        print("Pilihan tidak valid!")
                        continue
                except ValueError:
                    print("Masukkan angka yang valid!")
                    continue
            else:
                print(f"\n{'='*30}")
                print(f"GILIRAN {enemy.name}")
                print(f"{'='*30}")
                
                if special_effects["dodge"]:
                    dodge_chance = player.speed / (player.speed + enemy.speed) * 0.3
                    if random.random() < dodge_chance:
                        print(f"{enemy.name} menyerang, tapi kamu berhasil menghindar!")
                        special_effects["dodge"] = False
                    else:
                        damage = max(1, enemy.attack - player.defense // 2)
                        if special_effects["mana_shield"]:
                            damage = max(1, damage // 2)
                            print("Perisai mana mengurangi damage!")
                        player.current_hp -= damage
                        print(f"{enemy.name} menyerangmu dan menyebabkan {damage} damage!")
                        special_effects["dodge"] = False
                else:
                    damage = max(1, enemy.attack - player.defense // 2)
                    if special_effects["mana_shield"]:
                        damage = max(1, damage // 2)
                        print("Perisai mana mengurangi damage!")
                    player.current_hp -= damage
                    print(f"{enemy.name} menyerangmu dan menyebabkan {damage} damage!")
                
                if player.current_hp <= 0:
                    print("Kamu kalah dalam pertempuran...")
                    battle_ongoing = False
                    return False
            
            if 'poison' in enemy.effects and enemy.effects['poison'] > 0:
                poison_damage = max(1, enemy.max_hp // 10)
                enemy.current_hp -= poison_damage
                print(f"Racun menyebabkan {poison_damage} damage pada {enemy.name}!")
                enemy.effects['poison'] -= 1
                if enemy.effects['poison'] == 0:
                    del enemy.effects['poison']
                if enemy.current_hp <= 0:
                    print(f"{enemy.name} mati karena racun!")
                    player.battle_wins += 1
                    player.check_ras_unlocks()
                    battle_ongoing = False
                    return True
            
            if special_effects["boost_attack"] > 0:
                special_effects["boost_attack"] -= 1
            if special_effects["critical_boost"] > 0:
                special_effects["critical_boost"] -= 1
            
            print(f"\n--- Status ---")
            print(f"{player.name}: {player.current_hp}/{player.max_hp} HP | {player.mana}/{player.max_mana} MP")
            print(f"{enemy.name}: {enemy.current_hp}/{enemy.max_hp} HP")
            
            player_turn = not player_turn
        
        return False
    except Exception as e:
        print(f"Error dalam sistem pertempuran: {e}")
        return False

def save_game(player):
    try:
        save_data = {
            "player": {
                "name": player.name,
                "max_hp": player.max_hp,
                "current_hp": player.current_hp,
                "attack": player.attack,
                "defense": player.defense,
                "speed": player.speed,
                "durability": player.durability,
                "luck": player.luck,
                "mana": player.mana,
                "max_mana": player.max_mana,
                "equipped_artefaks": player.equipped_artefaks,
                "inventory": player.inventory,
                "completed_quests": player.completed_quests,
                "current_location": player.current_location,
                "game_time": player.game_time,
                "ras": player.ras,
                "unlocked_ras": player.unlocked_ras,
                "battle_wins": player.battle_wins,
                "player_class": player.player_class,
                "save_timestamp": datetime.now().isoformat()
            }
        }
        with open("savegame.json", "w", encoding='utf-8') as file:
            json.dump(save_data, file, indent=2, ensure_ascii=False)
        print("\nGame berhasil disimpan!")
        return True
    except Exception as e:
        print(f"Error menyimpan game: {e}")
        return False

def load_game():
    try:
        if not os.path.exists("savegame.json"):
            print("\nTidak ada file save game ditemukan!")
            return None
        
        with open("savegame.json", "r", encoding='utf-8') as file:
            save_data = json.load(file)
        
        if "player" not in save_data:
            print("\nFormat save game tidak valid!")
            return None
        
        player_data = save_data["player"]
        player = Player(player_data["name"])
        player.max_hp = player_data.get("max_hp", 100)
        player.current_hp = player_data.get("current_hp", player.max_hp)
        player.attack = player_data.get("attack", 10)
        player.defense = player_data.get("defense", 5)
        player.speed = player_data.get("speed", 8)
        player.durability = player_data.get("durability", 6)
        player.luck = player_data.get("luck", 5)
        player.mana = player_data.get("mana", 50)
        player.max_mana = player_data.get("max_mana", 50)
        player.equipped_artefaks = player_data.get("equipped_artefaks", [])
        player.inventory = player_data.get("inventory", [])
        player.completed_quests = player_data.get("completed_quests", [])
        player.current_location = player_data.get("current_location", "Desa Awal")
        player.game_time = player_data.get("game_time", "00:00:00")
        player.ras = player_data.get("ras", "Jawa")
        player.unlocked_ras = player_data.get("unlocked_ras", ["Jawa"])
        player.battle_wins = player_data.get("battle_wins", 0)
        player.player_class = player_data.get("player_class", "Fighter")
        
        for artefak in player.equipped_artefaks:
            if artefak in ARTEFAK_DATABASE:
                player.apply_artefak_effects(artefak)
        
        player.apply_class_bonus()
        player.skills = player.get_class_skills()
        
        print("\nGame berhasil dimuat!")
        return player
    except Exception as e:
        print(f"Error memuat game: {e}")
        return None

def display_main_menu():
    print("\n" + "="*50)
    print("MIMPI PERANG ARTEFAK")
    print("="*50)
    print("1. Mulai Petualangan Baru")
    print("2. Muat Game")
    print("3. Keluar")
    print("="*50)

def display_game_menu():
    print("\n" + "="*30)
    print("MENU UTAMA")
    print("="*30)
    print("1. Ganti Lokasi")
    print("2. Cari Pertempuran")
    print("3. Inventory Artefak")
    print("4. Lihat Statistik")
    print("5. Kelola Ras")
    print("6. Kelola Class")
    print("7. Simpan Game")
    print("8. Kembali ke Menu Utama")
    print("="*30)

def display_class_menu(player):
    print("\n" + "="*40)
    print("KELOLA CLASS")
    print("="*40)
    print(f"Class Aktif: {player.player_class}")
    print("\nClass yang tersedia:")
    for i, class_name in enumerate(CLASS_BONUS.keys(), 1):
        bonus = CLASS_BONUS.get(class_name, {})
        bonus_text = ", ".join([f"{k}: +{v}" for k, v in bonus.items()])
        print(f"{i}. {class_name} - {bonus_text}")
    print("\n1. Ganti Class")
    print("2. Lihat Skills")
    print("3. Kembali")
    try:
        choice = int(input("Pilihan (1-3): "))
        if choice == 1:
            print("\nPilih class:")
            classes = list(CLASS_BONUS.keys())
            for i, class_name in enumerate(classes, 1):
                print(f"{i}. {class_name}")
            try:
                class_choice = int(input("Pilihan: ")) - 1
                if 0 <= class_choice < len(classes):
                    new_class = classes[class_choice]
                    if player.change_class(new_class):
                        print(f"\nClass berhasil diganti menjadi {new_class}!")
                    else:
                        print("\nGagal mengganti class!")
                else:
                    print("\nPilihan tidak valid!")
            except ValueError:
                print("\nMasukkan angka yang valid!")
        elif choice == 2:
            player.display_skills()
        elif choice == 3:
            return
        else:
            print("\nPilihan tidak valid!")
    except ValueError:
        print("\nMasukkan angka yang valid!")

def display_ras_menu(player):
    print("\n" + "="*40)
    print("KELOLA RAS")
    print("="*40)
    print(f"Ras Aktif: {player.ras}")
    print("\nRas yang tersedia:")
    for i, ras in enumerate(player.unlocked_ras, 1):
        bonus = RAS_BONUS.get(ras, {})
        bonus_text = ", ".join([f"{k}: +{v}" for k, v in bonus.items()])
        print(f"{i}. {ras} - {bonus_text}")
    print("\nRas terkunci:")
    locked_ras = [ras for ras in RAS_BONUS.keys() if ras not in player.unlocked_ras]
    for ras in locked_ras:
        requirement = RAS_UNLOCK_REQUIREMENTS.get(ras, "?")
        print(f"   {ras} - {requirement}")
    print("\n1. Ganti Ras")
    print("2. Kembali")
    try:
        choice = int(input("Pilihan (1-2): "))
        if choice == 1:
            if len(player.unlocked_ras) > 1:
                print("\nPilih ras:")
                for i, ras in enumerate(player.unlocked_ras, 1):
                    print(f"{i}. {ras}")
                try:
                    ras_choice = int(input("Pilihan: ")) - 1
                    if 0 <= ras_choice < len(player.unlocked_ras):
                        new_ras = player.unlocked_ras[ras_choice]
                        if player.change_ras(new_ras):
                            print(f"\nRas berhasil diganti menjadi {new_ras}!")
                        else:
                            print("\nGagal mengganti ras!")
                    else:
                        print("\nPilihan tidak valid!")
                except ValueError:
                    print("\nMasukkan angka yang valid!")
            else:
                print("\nHanya memiliki 1 ras yang terbuka!")
        elif choice == 2:
            return
        else:
            print("\nPilihan tidak valid!")
    except ValueError:
        print("\nMasukkan angka yang valid!")

def display_artefak_details(artefak_name):
    """Display detailed information about an artifact including its cultural origins"""
    if artefak_name not in ARTEFAK_DATABASE:
        print("\nArtefak tidak ditemukan!")
        return
    
    artefak_data = ARTEFAK_DATABASE[artefak_name]
    
    print(f"\n{'='*60}")
    print(f"DETAIL ARTEFAK: {artefak_name.upper()}")
    print(f"{'='*60}")
    print(f"Tipe: {artefak_data['type'].capitalize()} ({artefak_data['rarity'].upper()})")
    
    # Display stats
    stats = artefak_data.get('stats', {})
    if stats:
        print("\nStat Bonus:")
        for stat, value in stats.items():
            stat_name = stat.replace('_', ' ').title()
            sign = '+' if value > 0 else ''
            print(f"  {stat_name}: {sign}{value}")
    
    # Display effect if exists
    effect = artefak_data.get('effect')
    if effect:
        print("\nEfek Khusus:")
        if "condition" in effect:
            condition_text = {
                "enemy_hp_above_50": "Jika HP musuh > 50%",
                "player_hp_below_30": "Jika HP pemain < 30%",
                "always": "Selalu aktif",
                "first_attack": "Pada serangan pertama",
                "enemy_hp_full": "Jika musuh memiliki HP penuh"
            }.get(effect["condition"], effect["condition"])
            print(f"  Kondisi: {condition_text}")
        
        if "damage" in effect:
            damage_text = {
                "extra_10_percent": "Damage tambahan 10% dari max HP musuh",
                "double_damage": "Double damage pada serangan berikutnya",
                "bonus_5": "Bonus 5 damage",
                "25_percent_max_hp": "Damage sebesar 25% dari max HP musuh"
            }.get(effect["damage"], effect["damage"])
            print(f"  Efek: {damage_text}")
        
        if "effect" in effect:
            effect_text = {
                "first_strike": "Memberikan first strike di awal pertempuran",
                "royal_aura": "Aura kerajaan meningkatkan semua stat",
                "rhythm_bonus": "Bonus ritme meningkatkan mana dan luck"
            }.get(effect["effect"], effect["effect"])
            print(f"  Efek: {effect_text}")
    
    # Display cultural description
    print(f"\n{'-'*60}")
    print("DESKRIPSI BUDAYA:")
    print(f"{'-'*60}")
    print(f"{artefak_data['description']}")
    print(f"\n{'-'*60}")
    print("MAKNA BUDAYA:")
    print(f"{'-'*60}")
    print(f"{artefak_data['cultural_significance']}")
    print(f"{'='*60}")

def display_inventory(player):
    print("\n" + "="*40)
    print("INVENTORY ARTEFAK")
    print("="*40)
    print(f"Artefak Terpasang [{len(player.equipped_artefaks)}/7]:")
    for i, artefak in enumerate(player.equipped_artefaks, 1):
        artefak_data = ARTEFAK_DATABASE[artefak]
        print(f"  {i}. {artefak} ({artefak_data['rarity'].upper()})")
    print(f"\nArtefak dalam Inventory [{len(player.inventory)}]:")
    for i, artefak in enumerate(player.inventory, 1):
        artefak_data = ARTEFAK_DATABASE[artefak]
        print(f"  {i}. {artefak} ({artefak_data['rarity'].upper()})")
    print("\n1. Pasang Artefak")
    print("2. Lepas Artefak") 
    print("3. Lihat Detail Artefak")
    print("4. Kembali")
    try:
        choice = int(input("Pilihan (1-4): "))
        if choice == 1:
            if len(player.equipped_artefaks) >= 7:
                print("\nSlot artefak penuh! Maksimal 7 artefak.")
                return
            if not player.inventory:
                print("\nInventory kosong!")
                return
            
            print("\nPilih artefak untuk dipasang:")
            for i, artefak in enumerate(player.inventory, 1):
                artefak_data = ARTEFAK_DATABASE[artefak]
                print(f"{i}. {artefak} ({artefak_data['rarity'].upper()})")
            
            try:
                artefak_choice = int(input("Pilihan: ")) - 1
                selected_artefak = player.inventory[artefak_choice]
                if player.equip_artefak(selected_artefak):
                    print(f"\n{selected_artefak} berhasil dipasang!")
                else:
                    print("\nGagal mempasang artefak!")
            except (ValueError, IndexError):
                print("\nPilihan tidak valid!")
        elif choice == 2:
            if not player.equipped_artefaks:
                print("\nTidak ada artefak yang terpasang!")
                return
            
            print("\nPilih artefak untuk dilepas:")
            for i, artefak in enumerate(player.equipped_artefaks, 1):
                artefak_data = ARTEFAK_DATABASE[artefak]
                print(f"{i}. {artefak} ({artefak_data['rarity'].upper()})")
            
            try:
                artefak_choice = int(input("Pilihan: ")) - 1
                selected_artefak = player.equipped_artefaks[artefak_choice]
                if player.unequip_artefak(selected_artefak):
                    print(f"\n{selected_artefak} berhasil dilepas!")
                else:
                    print("\nGagal melepas artefak!")
            except (ValueError, IndexError):
                print("\nPilihan tidak valid!")
        elif choice == 3:
            all_artefaks = player.equipped_artefaks + player.inventory
            if not all_artefaks:
                print("\nTidak ada artefak untuk dilihat!")
                return
            
            print("\nPilih artefak untuk melihat detail:")
            for i, artefak in enumerate(all_artefaks, 1):
                artefak_data = ARTEFAK_DATABASE[artefak]
                status = "(Terpasang)" if artefak in player.equipped_artefaks else "(Di Inventory)"
                print(f"{i}. {artefak} {status}")
            
            try:
                artefak_choice = int(input("Pilihan: ")) - 1
                selected_artefak = all_artefaks[artefak_choice]
                display_artefak_details(selected_artefak)
            except (ValueError, IndexError):
                print("\nPilihan tidak valid!")
        elif choice == 4:
            return
        else:
            print("\nPilihan tidak valid!")
    except ValueError:
        print("\nMasukkan angka yang valid!")

def change_location(player):
    locations = [
        "Hutan Misterius", "Gua Terlarang", "Danau Ajaib", 
        "Gunung Berapi", "Kota Tua", "Istana Kerajaan"
    ]
    print("\n" + "="*50)
    print("PILIH LOKASI UNTUK DIJELAJAHI")
    print("="*50)
    for i, location in enumerate(locations, 1):
        print(f"{i}. {location}")
    print("="*50)
    
    try:
        choice = int(input("Pilihan (1-6): "))
        if 1 <= choice <= len(locations):
            new_location = locations[choice - 1]
            player.current_location = new_location
            player.game_time = datetime.now().strftime("%H:%M:%S")
            print(f"\nKamu sekarang berada di: {new_location}")
            return True
        else:
            print("\nPilihan tidak valid!")
            return False
    except ValueError:
        print("\nMasukkan angka yang valid!")
        return False

def find_battle(player):
    try:
        locations = [
            "Hutan Misterius", "Gua Terlarang", "Danau Ajaib", 
            "Gunung Berapi", "Kota Tua", "Istana Kerajaan"
        ]
        if player.current_location not in locations:
            print("\nLokasi tidak valid!")
            return False
        
        enemy_types = {
            "Hutan Misterius": ["Serigala Liar", "Penyihir Hutan", "Guardian Hutan", "Ular Raksasa"],
            "Gua Terlarang": ["Kelelawar Gua", "Goblin Gua", "Raksasa Batu", "Naga Kecil"],
            "Danau Ajaib": ["Ikan Raksasa", "Roh Air", "Nyi Roro Kidul", "Katak Ajaib"],
            "Gunung Berapi": ["Elemental Api", "Raksasa Lava", "Burung Api", "Dewa Api"],
            "Kota Tua": ["Pencuri", "Ksatria Tua", "Raja Kota", "Penyihir Kota"],
            "Istana Kerajaan": ["Penjaga Istana", "Penyihir Kerajaan", "Pengawal Elit", "Raja Terakhir"]
        }
        
        enemy_name = random.choice(enemy_types[player.current_location])
        enemy_level = random.randint(1, 5)
        enemy = Enemy(enemy_name, enemy_level)
        
        if enemy_name == "Guardian Hutan":
            enemy.artefak_drop = random.choice(["Mandau", "Perisai Talawang"])
            enemy.drop_chance = 0.8
        elif enemy_name == "Nyi Roro Kidul":
            enemy.artefak_drop = "Gamelan Mini"
            enemy.drop_chance = 0.7
        elif enemy_name == "Dewa Api":
            enemy.artefak_drop = "Trisula"
            enemy.drop_chance = 0.7
        elif enemy_name == "Raja Kota":
            enemy.artefak_drop = "Siger"
            enemy.drop_chance = 0.7
        elif enemy_name == "Raja Terakhir":
            enemy.artefak_drop = "Kris"
            enemy.drop_chance = 0.9
        
        print(f"\n{'='*50}")
        print(f"MUSUH MUNCUL DI {player.current_location.upper()}")
        print(f"{'='*50}")
        print(f"Kamu bertemu dengan {enemy.name} level {enemy_level}!")
        
        victory = battle_system(player, enemy)
        
        if victory:
            print(f"\n{'='*50}")
            print("KEMENANGAN")
            print(f"{'='*50}")
            print(f"Kamu mengalahkan {enemy.name}!")
            
            if enemy_name == "Guardian Hutan" and "Guardian Hutan" not in player.completed_quests:
                player.completed_quests.append("Guardian Hutan")
                print("Quest 'Kalahkan Guardian Hutan' selesai!")
            elif enemy_name == "Nyi Roro Kidul" and "Quest Seni" not in player.completed_quests:
                player.completed_quests.append("Quest Seni")
                print("Quest 'Selesaikan Quest Seni' selesai!")
            
            if enemy.artefak_drop and random.random() < enemy.drop_chance:
                found_artefak = enemy.artefak_drop
                if found_artefak not in player.equipped_artefaks and found_artefak not in player.inventory:
                    player.inventory.append(found_artefak)
                    print(f"{enemy.name} menjatuhkan {found_artefak}!")
            
            player.current_hp = min(player.max_hp, player.current_hp + 15)
            player.mana = min(player.max_mana, player.mana + 10)
            print("HP dan Mana dipulihkan sebagian setelah pertempuran.")
            player.check_ras_unlocks()
        else:
            print(f"\n{'='*50}")
            print("KEKALAHAN")
            print(f"{'='*50}")
            print("Kamu kembali untuk memulihkan diri...")
            player.current_hp = player.max_hp // 2
            player.mana = player.max_mana // 2
        
        return victory
    except Exception as e:
        print(f"Error dalam pertempuran: {e}")
        return False

def main():
    player = None
    game_active = True
    
    while game_active:
        display_main_menu()
        
        try:
            choice = int(input("Pilihan (1-3): "))
            if choice == 1:
                name = input("Masukkan nama pahlawan: ").strip()
                if not name:
                    print("\nNama tidak boleh kosong!")
                    continue
                
                player = Player(name)
                starter_artefaks = ["Tombak", "Perisai Talawang", "Destar"]
                for artefak in starter_artefaks:
                    if artefak in ARTEFAK_DATABASE:
                        player.inventory.append(artefak)
                        player.equip_artefak(artefak)
                
                print(f"\n{'='*50}")
                print(f"SELAMAT DATANG, {player.name.upper()}!")
                print(f"{'='*50}")
                print("Kamu memulai petualangan dengan 3 artefak starter.")
                print(f"Class default: {player.player_class}")
                print(f"Ras default: {player.ras}")
                print(f"Kamu berada di: {player.current_location}")
                print(f"{'='*50}")
                break
            elif choice == 2:
                player = load_game()
                if player:
                    break
                else:
                    continue
            elif choice == 3:
                confirm = input("Yakin ingin keluar? (y/n): ").lower()
                if confirm == 'y':
                    print("\nTerima kasih telah bermain!")
                    return
            else:
                print("\nPilihan tidak valid!")
        except ValueError:
            print("\nMasukkan angka yang valid!")
        except KeyboardInterrupt:
            print("\n\nGame dihentikan oleh user.")
            return
    
    while player and game_active:
        try:
            # Always display stats first
            player.display_stats()
            display_game_menu()
            
            choice = int(input("Pilihan (1-8): "))
            if choice == 1:
                change_location(player)
            elif choice == 2:
                find_battle(player)
            elif choice == 3:
                display_inventory(player)
            elif choice == 4:
                player.display_stats()
                set_bonus = player.get_artefak_set_bonus()
                if set_bonus:
                    print("\nBONUS SET ARTEFAK:")
                    for set_name, bonuses in set_bonus.items():
                        print(f"  {set_name}: {bonuses}")
            elif choice == 5:
                display_ras_menu(player)
            elif choice == 6:
                display_class_menu(player)
            elif choice == 7:
                save_game(player)
            elif choice == 8:
                save_option = input("Simpan game sebelum keluar? (y/n): ").lower()
                if save_option == 'y':
                    save_game(player)
                print("\nKembali ke menu utama...")
                break
            else:
                print("\nPilihan tidak valid!")
        except ValueError:
            print("\nMasukkan angka yang valid!")
        except KeyboardInterrupt:
            print("\n\nGame dihentikan. Menyimpan...")
            save_game(player)
            game_active = False
        except Exception as e:
            print(f"\nError tidak terduga: {e}")
            continue

if __name__ == "__main__":
    while True:
        main()
        restart = input("\nMain lagi? (y/n): ").lower()
        if restart != 'y':
            print("\nTerima kasih telah bermain Mimpi Perang Artefak!")
            break