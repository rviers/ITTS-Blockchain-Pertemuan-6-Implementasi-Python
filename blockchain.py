import hashlib
import json
import time

class Block:
    def __init__(self, index, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Menghitung hash SHA-256 dari seluruh isi blok secara deterministik."""
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()

    def __repr__(self):
        return (f"Block(Index: {self.index}, Hash: {self.hash[:16]}..., "
                f"PrevHash: {self.previous_hash[:16]}..., Data: {self.data})")


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        """Membuat genesis block (blok ke-0) secara otomatis."""
        genesis_block = Block(
            index=0,
            data={"keterangan": "Genesis Block ITTS Blockchain"},
            previous_hash="0" * 64
        )
        return genesis_block

    def latest_block(self):
        """Mengambil blok terakhir dalam rantai."""
        return self.chain[-1]

    def add_block(self, data):
        """Menambahkan blok baru ke rantai dengan previous_hash dari blok terakhir."""
        prev_block = self.latest_block()
        new_block = Block(
            index=len(self.chain),
            data=data,
            previous_hash=prev_block.hash
        )
        self.chain.append(new_block)
        return new_block

    def is_valid(self):
        """
        Validasi integritas blockchain:
        1. Hash internal blok sesuai dengan kalkulasi ulang data blok.
        2. previous_hash setiap blok cocok dengan hash blok sebelumnya.
        """
        # Cek integritas genesis block
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.previous_hash != "0" * 64:
            return False
        if genesis.hash != genesis.calculate_hash():
            return False

        # Cek blok selanjutnya
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # 1. Cek apakah hash blok saat ini telah dimanipulasi (internal integrity)
            if current.hash != current.calculate_hash():
                return False

            # 2. Cek apakah linkage previous_hash terputus (chain linkage)
            if current.previous_hash != previous.hash:
                return False

        return True


def run_tests():
    print("=" * 70)
    print("PENGUJIAN IMPLEMENTASI BLOCKCHAIN SEDERHANA PYTHON - TUGAS 4 ITTS")
    print("=" * 70)

    # -------------------------------------------------------------
    # Skenario 1: Chain baru hanya memiliki genesis block
    # -------------------------------------------------------------
    print("\n[SKENARIO 1] Inisialisasi Chain & Genesis Block")
    bc = Blockchain()
    print(f"Jumlah blok saat ini : {len(bc.chain)}")
    print(f"Genesis Block Index  : {bc.chain[0].index}")
    print(f"Genesis Prev Hash    : {bc.chain[0].previous_hash}")
    print(f"Genesis Block Hash   : {bc.chain[0].hash}")
    valid_s1 = bc.is_valid()
    print(f"Status Validasi Chain: {'VALID (True)' if valid_s1 else 'TIDAK VALID (False)'}")
    assert valid_s1 is True, "Skenario 1 Gagal!"

    # -------------------------------------------------------------
    # Skenario 2: Tambah minimal 3 block dengan transaksi berbeda
    # -------------------------------------------------------------
    print("\n[SKENARIO 2] Menambahkan 3 Blok Transaksi Berbeda")
    t1 = {"pengirim": "Alice", "penerima": "Bob", "nominal": 50, "token": "IDR"}
    t2 = {"pengirim": "Bob", "penerima": "Charlie", "nominal": 20, "token": "IDR"}
    t3 = {"pengirim": "Charlie", "penerima": "Dave", "nominal": 15, "token": "IDR"}

    b1 = bc.add_block(t1)
    b2 = bc.add_block(t2)
    b3 = bc.add_block(t3)
    print(f"Blok 1 ditambahkan: Data={b1.data}, Hash={b1.hash[:20]}...")
    print(f"Blok 2 ditambahkan: Data={b2.data}, Hash={b2.hash[:20]}...")
    print(f"Blok 3 ditambahkan: Data={b3.data}, Hash={b3.hash[:20]}...")
    print(f"Total blok sekarang: {len(bc.chain)}")
    valid_s2 = bc.is_valid()
    print(f"Status Validasi Chain: {'VALID (True)' if valid_s2 else 'TIDAK VALID (False)'}")
    assert valid_s2 is True, "Skenario 2 Gagal!"

    # -------------------------------------------------------------
    # Skenario 3: Ubah data pada block tengah tanpa hitung ulang chain
    # -------------------------------------------------------------
    print("\n[SKENARIO 3] Tampering Data pada Blok Tengah (Block Index 2)")
    print(f"Data asli Block 2: {bc.chain[2].data}")
    # Manipulasi data transaksi
    bc.chain[2].data = {"pengirim": "Bob", "penerima": "Attacker", "nominal": 9999, "token": "IDR"}
    print(f"Data palsu Block 2: {bc.chain[2].data}")
    valid_s3 = bc.is_valid()
    print(f"Status Validasi Chain setelah Tampering Data: {'VALID (True)' if valid_s3 else 'TIDAK VALID (False)'}")
    assert valid_s3 is False, "Skenario 3 Gagal! Sistem gagal mendeteksi modifikasi data."

    # Kembalikan data asli untuk memulihkan validitas chain
    bc.chain[2].data = t2
    print("-> Data Block 2 dikembalikan ke kondisi asli.")
    valid_s3_restored = bc.is_valid()
    print(f"Status Validasi Chain pulih: {'VALID (True)' if valid_s3_restored else 'TIDAK VALID (False)'}")
    assert valid_s3_restored is True, "Pemulihan Skenario 3 Gagal!"

    # -------------------------------------------------------------
    # Skenario 4: Dua Varian Tampering previous_hash pada Block Index 2
    # -------------------------------------------------------------
    print("\n[SKENARIO 4] Tampering previous_hash pada Block (Block Index 2)")
    original_prev_hash = bc.chain[2].previous_hash
    original_hash = bc.chain[2].hash
    fake_prev_hash = "deadbeef" * 8

    # Varian 4A: previous_hash diubah TANPA menghitung ulang hash blok
    print("\n--- Skenario 4A: previous_hash diubah TANPA menghitung ulang hash blok ---")
    print(f"Previous Hash asli : {original_prev_hash}")
    bc.chain[2].previous_hash = fake_prev_hash
    print(f"Previous Hash palsu: {bc.chain[2].previous_hash}")
    print(f"Hash blok tetap    : {bc.chain[2].hash}")
    valid_s4a = bc.is_valid()
    print(f"Status Validasi Chain (4A): {'VALID (True)' if valid_s4a else 'TIDAK VALID (False)'}")
    assert valid_s4a is False, "Skenario 4A Gagal! Harus False karena hash internal tidak cocok."

    # Pulihkan chain ke kondisi valid setelah varian 4A
    bc.chain[2].previous_hash = original_prev_hash
    bc.chain[2].hash = original_hash
    valid_s4a_restored = bc.is_valid()
    print(f"-> Chain dipulihkan setelah 4A. Status: {'VALID (True)' if valid_s4a_restored else 'TIDAK VALID (False)'}")
    assert valid_s4a_restored is True, "Pemulihan setelah 4A Gagal!"

    # Varian 4B: previous_hash diubah DENGAN menghitung ulang hash blok
    print("\n--- Skenario 4B: previous_hash diubah DENGAN menghitung ulang hash blok ---")
    bc.chain[2].previous_hash = fake_prev_hash
    bc.chain[2].hash = bc.chain[2].calculate_hash()
    print(f"Previous Hash palsu: {bc.chain[2].previous_hash}")
    print(f"Hash dihitung ulang: {bc.chain[2].hash}")
    print("Hash internal blok 2 kini konsisten, namun keterikatan dengan blok 1 dan blok 3 terputus.")
    valid_s4b = bc.is_valid()
    print(f"Status Validasi Chain (4B): {'VALID (True)' if valid_s4b else 'TIDAK VALID (False)'}")
    assert valid_s4b is False, "Skenario 4B Gagal! Harus False karena relasi rantai terputus."

    # Pulihkan chain ke kondisi valid setelah varian 4B
    bc.chain[2].previous_hash = original_prev_hash
    bc.chain[2].hash = original_hash
    valid_s4b_restored = bc.is_valid()
    print(f"-> Chain dipulihkan setelah 4B. Status: {'VALID (True)' if valid_s4b_restored else 'TIDAK VALID (False)'}")
    assert valid_s4b_restored is True, "Pemulihan setelah 4B Gagal!"

    # -------------------------------------------------------------
    # Skenario 5: Cetak index, hash, dan previous_hash setiap block
    # -------------------------------------------------------------
    print("\n[SKENARIO 5] Cetak Rincian Seluruh Rantai Blockchain")
    print("-" * 70)
    for block in bc.chain:
        print(f"Index         : {block.index}")
        print(f"Timestamp     : {block.timestamp}")
        print(f"Data          : {block.data}")
        print(f"Previous Hash : {block.previous_hash}")
        print(f"Current Hash  : {block.hash}")
        print("-" * 70)

    print("\nSEMUA SKENARIO PENGUJIAN WAJIB BERHASIL DIEKSEKUSI DENGAN BENAR.\n")

if __name__ == "__main__":
    run_tests()
