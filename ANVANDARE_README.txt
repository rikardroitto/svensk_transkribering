╔═══════════════════════════════════════════════════════════════╗
║          WHISPER DIARIZE - SVENSK TRANSKRIBERING              ║
║         Lokal tal-till-text med talarseparation               ║
╚═══════════════════════════════════════════════════════════════╝

📖 SNABBSTART
═════════════════════════════════════════════════════════════════

1. Dubbelklicka på WhisperDiarize.exe
2. Webbläsaren öppnas automatiskt
3. Dra och släpp en ljudfil (mp3, wav, etc.)
4. Vänta medan filen bearbetas
5. Ladda ner resultatet!


⚡ SYSTEMKRAV
═════════════════════════════════════════════════════════════════

REKOMMENDERAT (för snabb bearbetning):
  ✓ Windows 10/11 (64-bit)
  ✓ NVIDIA grafikkort (GTX 1060 eller nyare)
  ✓ NVIDIA driver 525.60.13 eller nyare
  ✓ 8GB RAM (16GB rekommenderat)

MINIMUM (långsammare):
  ✓ Windows 10/11 (64-bit)
  ✓ 8GB RAM
  ⚠️ Utan NVIDIA GPU: 5-10x långsammare


⏱️ FÖRVÄNTAD BEARBETNINGSTID
═════════════════════════════════════════════════════════════════

3 minuters ljudfil:
  • Med GPU: ~30 sekunder
  • Utan GPU: ~3-5 minuter


🔧 FELSÖKNING
═════════════════════════════════════════════════════════════════

❌ "Windows skyddade din dator"
   → Klicka "Mer info" → "Kör ändå"
   (Programmet är osignerat men säkert)

❌ "Programmet kan inte starta eftersom..."
   → Installera Microsoft Visual C++ Redistributable:
   → https://aka.ms/vs/17/release/vc_redist.x64.exe

❌ GPU fungerar inte / Långsam bearbetning
   → Kontrollera att du har NVIDIA-kort i Enhetshanteraren
   → Uppdatera NVIDIA driver: https://www.nvidia.com/drivers
   → Programmet fungerar ändå, men långsammare på CPU

❌ Webbläsaren öppnas inte automatiskt
   → Öppna manuellt: http://127.0.0.1:5000

❌ "Diarisering misslyckades"
   → Första gången: Behöver ladda ner modeller (~1.5GB)
   → Kräver internetanslutning första körningen
   → Därefter fungerar det offline


📁 VAD ÄR DIARISERING?
═════════════════════════════════════════════════════════════════

Diarisering = Identifierar VILKA som pratar ("Talare 1", "Talare 2")
Transkribering = Konverterar tal till text

Resultatet visar vem som sa vad:

    [SPEAKER_00] Hej, hur mår du?
    [SPEAKER_01] Jag mår bra, tack!


🔒 INTEGRITET
═════════════════════════════════════════════════════════════════

✓ Allt bearbetas LOKALT på din dator
✓ Inga ljudfiler skickas till internet
✓ Dina filer lämnar aldrig din dator
✓ Inga konton eller inloggningar behövs

OBS: Första körningen laddar ner AI-modeller från internet,
men själva transkriberingen sker offline.


📄 OUTPUT-FORMAT
═════════════════════════════════════════════════════════════════

Du kan välja mellan:
  • TXT - Enkel text med talarnamn
  • SRT - Undertextformat med tidsmarkeringar
  • JSON - Strukturerad data för vidare bearbetning
  • TSV - Tabell-format för Excel/spreadsheets


💾 VAR SPARAS FILERNA?
═════════════════════════════════════════════════════════════════

Output-filer sparas i:
  C:\Users\[ditt-användarnamn]\WhisperDiarize\


🌐 SPRÅK
═════════════════════════════════════════════════════════════════

Optimerat för SVENSKA, men fungerar även med:
  • Engelska
  • Norska
  • Danska
  • Och 90+ andra språk


📞 SUPPORT
═════════════════════════════════════════════════════════════════

Problem? Frågor?
→ Skapa en issue på GitHub
→ [lägg till din kontaktinfo eller support-länk här]


═════════════════════════════════════════════════════════════════
         Gjord med ❤️ för svensk tal-till-text
═════════════════════════════════════════════════════════════════
