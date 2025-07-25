import streamlit as st
import ollama
import sqlite3
import pandas as pd

# Initialize SQLite database using Amazon dataset
def init_amazon_db():
    conn = sqlite3.connect(':memory:')  # In-memory database for demo
    cursor = conn.cursor()
    
    # Create Amazon table
    cursor.execute("""
    CREATE TABLE amazon (
        product_id TEXT,
        product_name TEXT,
        category TEXT,
        discounted_price TEXT,
        actual_price TEXT,
        discount_percentage NUMERIC,
        rating TEXT,
        rating_count INTEGER,
        about_product TEXT,
        user_id TEXT,
        user_name TEXT,
        review_id TEXT,
        review_title TEXT,
        review_content TEXT,
        img_link TEXT,
        product_link TEXT
    )
    """)
    
    # Insert sample data
    cursor.executemany("""
    INSERT INTO amazon VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ('P001', 'Product A', 'Electronics', '$100', '$120', 20, '4.5', 500, 'Good quality', 'U001', 'Alice', 'R001', 'Nice Product', 'Works well!', 'img_link', 'product_link'),
        ('P002', 'Product B', 'Books', '$15', '$20', 25, '4.2', 300, 'Bestseller book', 'U002', 'Bob', 'R002', 'Great Book', 'Loved it!', 'img_link', 'product_link')
    ])
    
    conn.commit()
    return conn

conn = init_amazon_db()

def generate_sql_query(nl_query):
    """Use Ollama to convert natural language to an SQL query with correct column names."""
    prompt = f"""
    Convert the following natural language request into a valid SQL query compatible with SQLite.
    Use the following table schema:
    Table: amazon
    Columns: product_id, product_name, category, discounted_price, actual_price, 
             discount_percentage, rating, rating_count, about_product, user_id, user_name,
             review_id, review_title, review_content, img_link, product_link

    Available category fileds: Computers&Accessories|Accessories&Peripherals|Cables&Accessories|Cables|USBCables
Computers&Accessories|NetworkingDevices|NetworkAdapters|WirelessUSBAdapters
Electronics|HomeTheater,TV&Video|Accessories|Cables|HDMICables
Electronics|HomeTheater,TV&Video|Televisions|SmartTelevisions
Electronics|HomeTheater,TV&Video|Accessories|RemoteControls
Electronics|HomeTheater,TV&Video|Televisions|StandardTelevisions
Electronics|HomeTheater,TV&Video|Accessories|TVMounts,Stands&Turntables|TVWall&CeilingMounts
Electronics|HomeTheater,TV&Video|Accessories|Cables|RCACables
Electronics|HomeAudio|Accessories|SpeakerAccessories|Mounts
Electronics|HomeTheater,TV&Video|Accessories|Cables|OpticalCables
Electronics|HomeTheater,TV&Video|Projectors
Electronics|HomeAudio|Accessories|Adapters
Electronics|HomeTheater,TV&Video|SatelliteEquipment|SatelliteReceivers
Computers&Accessories|Accessories&Peripherals|Cables&Accessories|Cables|DVICables
Electronics|HomeTheater,TV&Video|Accessories|Cables|SpeakerCables
Electronics|HomeAudio|MediaStreamingDevices|StreamingClients
Electronics|HomeTheater,TV&Video|AVReceivers&Amplifiers
Electronics|HomeAudio|Speakers|TowerSpeakers
Electronics|HomeTheater,TV&Video|Accessories|3DGlasses
Electronics|WearableTechnology|SmartWatches
Electronics|Mobiles&Accessories|MobileAccessories|Chargers|PowerBanks
Electronics|Mobiles&Accessories|Smartphones&BasicMobiles|Smartphones
Electronics|Accessories|MemoryCards|MicroSD
Electronics|Mobiles&Accessories|Smartphones&BasicMobiles|BasicMobiles
Electronics|Headphones,Earbuds&Accessories|Headphones|In-Ear
Electronics|Mobiles&Accessories|MobileAccessories|Chargers|AutomobileChargers
Electronics|Mobiles&Accessories|MobileAccessories|AutomobileAccessories|Cradles
Electronics|Mobiles&Accessories|MobileAccessories|Chargers|WallChargers
Electronics|Mobiles&Accessories|MobileAccessories|Cables&Adapters|OTGAdapters
Electronics|Mobiles&Accessories|MobileAccessories|Photo&VideoAccessories|Tripods
Electronics|Mobiles&Accessories|MobileAccessories|Photo&VideoAccessories|SelfieSticks
Electronics|Mobiles&Accessories|MobileAccessories|Stands
Computers&Accessories|Accessories&Peripherals|Cables&Accessories|CableConnectionProtectors
Electronics|Mobiles&Accessories|MobileAccessories|Décor
Electronics|Mobiles&Accessories|MobileAccessories|Maintenance,Upkeep&Repairs|ScreenProtectors
Electronics|Mobiles&Accessories|MobileAccessories|StylusPens
Electronics|Mobiles&Accessories|MobileAccessories|Mounts|Bedstand&DeskMounts
Electronics|Mobiles&Accessories|MobileAccessories|Cases&Covers|BasicCases
Electronics|Mobiles&Accessories|MobileAccessories|Mounts|HandlebarMounts
Electronics|Headphones,Earbuds&Accessories|Headphones|On-Ear
Computers&Accessories|Accessories&Peripherals|LaptopAccessories|CameraPrivacyCovers
Electronics|Headphones,Earbuds&Accessories|Adapters
Electronics|Mobiles&Accessories|MobileAccessories|Décor|PhoneCharms
Electronics|Mobiles&Accessories|MobileAccessories|Mounts|Shower&WallMounts
Computers&Accessories|ExternalDevices&DataStorage|PenDrives
Computers&Accessories|Accessories&Peripherals|Keyboards,Mice&InputDevices|Mice
Computers&Accessories|Accessories&Peripherals|Keyboards,Mice&InputDevices|GraphicTablets
Computers&Accessories|Accessories&Peripherals|LaptopAccessories|Lapdesks
Computers&Accessories|Accessories&Peripherals|LaptopAccessories|NotebookComputerStands
Computers&Accessories|Accessories&Peripherals|Keyboards,Mice&InputDevices|Keyboards
MusicalInstruments|Microphones|Condenser
Electronics|GeneralPurposeBatteries&BatteryChargers|DisposableBatteries
OfficeProducts|OfficePaperProducts|Paper|Stationery|Pens,Pencils&WritingSupplies|Pens&Refills|GelInkRollerballPens
Home&Kitchen|CraftMaterials|Scrapbooking|Tape
Computers&Accessories|Accessories&Peripherals|Keyboards,Mice&InputDevices|Keyboard&MouseSets
Computers&Accessories|ExternalDevices&DataStorage|ExternalHardDisks
Electronics|Cameras&Photography|VideoCameras
Electronics|Cameras&Photography|Accessories|Tripods&Monopods|Tabletop&TravelTripods
OfficeProducts|OfficeElectronics|Calculators|Scientific
Computers&Accessories|NetworkingDevices|Repeaters&Extenders
Electronics|Cameras&Photography|Accessories|Tripods&Monopods|TripodLegs
Computers&Accessories|Printers,Inks&Accessories|Inks,Toners&Cartridges|InkjetInkCartridges
Computers&Accessories|Accessories&Peripherals|Keyboards,Mice&InputDevices|Keyboard&MiceAccessories|DustCovers
Computers&Accessories|Accessories&Peripherals|PCGamingPeripherals|GamingMice
Home&Kitchen|CraftMaterials|PaintingMaterials|Paints
Computers&Accessories|Accessories&Peripherals|Keyboards,Mice&InputDevices|Keyboard&MiceAccessories|MousePads
Computers&Accessories|Accessories&Peripherals|HardDiskBags
Electronics|Cameras&Photography|Flashes|Macro&RinglightFlashes
Computers&Accessories|NetworkingDevices
Computers&Accessories|NetworkingDevices|Routers
Electronics|Headphones,Earbuds&Accessories|Headphones|Over-Ear
Electronics|HomeAudio|Speakers|BluetoothSpeakers
Electronics|GeneralPurposeBatteries&BatteryChargers
OfficeProducts|OfficePaperProducts|Paper|Stationery|Notebooks,WritingPads&Diaries|WireboundNotebooks
Electronics|GeneralPurposeBatteries&BatteryChargers|RechargeableBatteries
Computers&Accessories|NetworkingDevices|NetworkAdapters|BluetoothAdapters
Computers&Accessories|Accessories&Peripherals|Adapters|USBtoUSBAdapters
Electronics|Cameras&Photography|Accessories|Tripods&Monopods|CompleteTripodUnits
OfficeProducts|OfficePaperProducts|Paper|Stationery|Notebooks,WritingPads&Diaries|Notepads&MemoBooks
Electronics|Cameras&Photography|Accessories|Film
Computers&Accessories|Monitors
Computers&Accessories|Accessories&Peripherals|USBGadgets|Lamps
Electronics|Cameras&Photography|Accessories|Cleaners|CleaningKits
Electronics|Cameras&Photography|SecurityCameras|DomeCameras
Computers&Accessories|Accessories&Peripherals|TabletAccessories|ScreenProtectors
Computers&Accessories|Accessories&Peripherals|PCGamingPeripherals|Gamepads
OfficeProducts|OfficeElectronics|Calculators|Basic
Computers&Accessories|Accessories&Peripherals|USBHubs
Computers&Accessories|Accessories&Peripherals|Audio&VideoAccessories|PCMicrophones
Electronics|HomeAudio|Speakers|OutdoorSpeakers
Computers&Accessories|Accessories&Peripherals|LaptopAccessories|Bags&Sleeves|LaptopSleeves&Slipcases
Computers&Accessories|ExternalDevices&DataStorage|ExternalMemoryCardReaders
OfficeProducts|OfficePaperProducts|Paper|Stationery|Pens,Pencils&WritingSupplies|Pens&Refills|BottledInk
OfficeProducts|OfficePaperProducts|Paper|Stationery|Notebooks,WritingPads&Diaries|CompositionNotebooks
OfficeProducts|OfficePaperProducts|Paper|Stationery|Pens,Pencils&WritingSupplies|Pens&Refills|RetractableBallpointPens
Computers&Accessories|Accessories&Peripherals|Cables&Accessories|Cables|EthernetCables
Computers&Accessories|Components|Memory
Computers&Accessories|Accessories&Peripherals|UninterruptedPowerSupplies
Electronics|Headphones,Earbuds&Accessories|Cases
Electronics|Accessories|MemoryCards|SecureDigitalCards
Electronics|Mobiles&Accessories|MobileAccessories|Photo&VideoAccessories|Flashes&SelfieLights|SelfieLights
Computers&Accessories|Accessories&Peripherals|Audio&VideoAccessories|Webcams&VoIPEquipment|Webcams
Computers&Accessories|Accessories&Peripherals|LaptopAccessories|CoolingPads
Computers&Accessories|Accessories&Peripherals|LaptopAccessories
Computers&Accessories|Accessories&Peripherals|TabletAccessories|Stands
HomeImprovement|Electrical|Adapters&Multi-Outlets
OfficeProducts|OfficePaperProducts|Paper|Copy&PrintingPaper|ColouredPaper
Computers&Accessories|Components|InternalSolidStateDrives
Electronics|HomeAudio|Speakers|MultimediaSpeakerSystems
Computers&Accessories|NetworkingDevices|DataCards&Dongles
Computers&Accessories|Accessories&Peripherals|LaptopAccessories|LaptopChargers&PowerSupplies
Computers&Accessories|Accessories&Peripherals|Audio&VideoAccessories|PCSpeakers
Electronics|Cameras&Photography|Accessories|Batteries&Chargers|BatteryChargers
Computers&Accessories|Accessories&Peripherals|TabletAccessories|Bags,Cases&Sleeves|Cases
OfficeProducts|OfficePaperProducts|Paper|Stationery|Pens,Pencils&WritingSupplies|Pens&Refills|StickBallpointPens
Home&Kitchen|CraftMaterials|DrawingMaterials|DrawingMedia|Pencils|WoodenPencils
Computers&Accessories|Components|InternalHardDrives
Computers&Accessories|Printers,Inks&Accessories|Printers
Home&Kitchen|CraftMaterials|DrawingMaterials|DrawingMedia|Pens
Computers&Accessories|Accessories&Peripherals|Cables&Accessories|Cables|SATACables
Computers&Accessories|Accessories&Peripherals|Audio&VideoAccessories|PCHeadsets
Computers&Accessories|Accessories&Peripherals|PCGamingPeripherals|GamingKeyboards
Electronics|HomeAudio|Speakers|SoundbarSpeakers
Electronics|Headphones,Earbuds&Accessories|Earpads
Computers&Accessories|Printers,Inks&Accessories|Printers|InkjetPrinters
Toys&Games|Arts&Crafts|Drawing&PaintingSupplies|ColouringPens&Markers
Computers&Accessories|Accessories&Peripherals|PCGamingPeripherals|Headsets
Computers&Accessories|ExternalDevices&DataStorage|ExternalSolidStateDrives
Computers&Accessories|NetworkingDevices|NetworkAdapters|PowerLANAdapters
Computers&Accessories|Printers,Inks&Accessories|Inks,Toners&Cartridges|InkjetInkRefills&Kits
OfficeProducts|OfficePaperProducts|Paper|Stationery|Notebooks,WritingPads&Diaries
Electronics|Cameras&Photography|Accessories|PhotoStudio&Lighting|PhotoBackgroundAccessories|BackgroundSupports
OfficeProducts|OfficeElectronics|Calculators|Financial&Business
Electronics|PowerAccessories|SurgeProtectors
Computers&Accessories|Tablets
HomeImprovement|Electrical|CordManagement
Home&Kitchen|CraftMaterials|PaintingMaterials
Computers&Accessories|Printers,Inks&Accessories|Inks,Toners&Cartridges|TonerCartridges
OfficeProducts|OfficePaperProducts|Paper|Stationery|Pens,Pencils&WritingSupplies|Pens&Refills|LiquidInkRollerballPens
OfficeProducts|OfficePaperProducts|Paper|Stationery|Pens,Pencils&WritingSupplies|Pens&Refills|FountainPens
Computers&Accessories|Accessories&Peripherals|HardDriveAccessories|Caddies
Computers&Accessories|Laptops|TraditionalLaptops
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|Kettles&HotWaterDispensers|ElectricKettles
Home&Kitchen|Heating,Cooling&AirQuality|RoomHeaters|ElectricHeaters
Home&Kitchen|Heating,Cooling&AirQuality|RoomHeaters|FanHeaters
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Irons,Steamers&Accessories|LintShavers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|DigitalKitchenScales
Home&Kitchen|Kitchen&Dining|KitchenTools|ManualChoppers&Chippers|Choppers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|InductionCooktop
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|HandBlenders
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Irons,Steamers&Accessories|Irons|DryIrons
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|MixerGrinders
Home&Kitchen|Heating,Cooling&AirQuality|WaterHeaters&Geysers|InstantWaterHeaters
Home&Kitchen|Heating,Cooling&AirQuality|RoomHeaters
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|Kettles&HotWaterDispensers|Kettle&ToasterSets
Home&Kitchen|Heating,Cooling&AirQuality|WaterHeaters&Geysers|StorageWaterHeaters
Home&Kitchen|Heating,Cooling&AirQuality|WaterHeaters&Geysers|ImmersionRods
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|DeepFatFryers|AirFryers
Home&Kitchen|HomeStorage&Organization|LaundryOrganization|LaundryBaskets
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Irons,Steamers&Accessories|Irons|SteamIrons
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|JuicerMixerGrinders
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Vacuums&FloorCare|Vacuums|HandheldVacuums
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|EggBoilers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|SandwichMakers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|MiniFoodProcessors&Choppers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|DigitalKitchenScales|DigitalScales
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|VacuumSealers
Home&Kitchen|Heating,Cooling&AirQuality|Fans|CeilingFans
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Vacuums&FloorCare|Vacuums|CanisterVacuums
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|PressureWashers,Steam&WindowCleaners
Home&Kitchen|Heating,Cooling&AirQuality|RoomHeaters|HalogenHeaters
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|Pop-upToasters
Home&Kitchen|Heating,Cooling&AirQuality|RoomHeaters|HeatConvectors
Home&Kitchen|Kitchen&HomeAppliances|Coffee,Tea&Espresso|CoffeeGrinders|ElectricGrinders
Home&Kitchen|Heating,Cooling&AirQuality|Fans|ExhaustFans
Home&Kitchen|Kitchen&HomeAppliances|Coffee,Tea&Espresso|DripCoffeeMachines
Home&Kitchen|Kitchen&HomeAppliances|WaterPurifiers&Accessories|WaterPurifierAccessories
Home&Kitchen|Kitchen&HomeAppliances|WaterPurifiers&Accessories|WaterCartridges
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|Rice&PastaCookers
Car&Motorbike|CarAccessories|InteriorAccessories|AirPurifiers&Ionizers
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Vacuums&FloorCare|Vacuums|Wet-DryVacuums
Home&Kitchen|Heating,Cooling&AirQuality|AirPurifiers|HEPAAirPurifiers
Home&Kitchen|Kitchen&HomeAppliances|WaterPurifiers&Accessories|WaterFilters&Purifiers
Home&Kitchen|HomeStorage&Organization|LaundryOrganization|LaundryBags
Home&Kitchen|Kitchen&HomeAppliances|SewingMachines&Accessories|Sewing&EmbroideryMachines
Home&Kitchen|HomeStorage&Organization|LaundryOrganization|IroningAccessories|SprayBottles
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|HandMixers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|Mills&Grinders|WetGrinders
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|OvenToasterGrills
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|Juicers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances
Health&PersonalCare|HomeMedicalSupplies&Equipment|HealthMonitors|WeighingScales|DigitalBathroomScales
Home&Kitchen|Kitchen&HomeAppliances|Coffee,Tea&Espresso|EspressoMachines
Home&Kitchen|Heating,Cooling&AirQuality|Fans|TableFans
Home&Kitchen|Kitchen&HomeAppliances|Coffee,Tea&Espresso|MilkFrothers
Home&Kitchen|Heating,Cooling&AirQuality|Humidifiers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|SmallApplianceParts&Accessories|StandMixerAccessories
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Vacuums&FloorCare|Vacuums|RoboticVacuums
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|YogurtMakers
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|Juicers|ColdPressJuicers
Home&Kitchen|Heating,Cooling&AirQuality|AirConditioners|Split-SystemAirConditioners
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|SmallApplianceParts&Accessories
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|WaffleMakers&Irons
Home&Kitchen|Kitchen&HomeAppliances|Coffee,Tea&Espresso|StovetopEspressoPots
Home&Kitchen|Kitchen&HomeAppliances|Coffee,Tea&Espresso|CoffeeMakerAccessories|MeasuringSpoons
Home&Kitchen|Kitchen&HomeAppliances|Coffee,Tea&Espresso|CoffeePresses
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|RotiMakers
Home&Kitchen|Heating,Cooling&AirQuality|Parts&Accessories|FanParts&Accessories
Home&Kitchen|Kitchen&HomeAppliances|SmallKitchenAppliances|StandMixers
Home&Kitchen|Heating,Cooling&AirQuality|Fans|PedestalFans
Home&Kitchen|Kitchen&HomeAppliances|Vacuum,Cleaning&Ironing|Vacuums&FloorCare|VacuumAccessories|VacuumBags|HandheldBags

    
    Request: "{nl_query}"
    """
    response = ollama.chat(model='dost', messages=[{"role": "user", "content": prompt}])
    sql_query = response['message']['content'].strip()
    return sql_query

def execute_query(query):
    """Execute an SQL query and return results as a DataFrame."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Fetch column names
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=columns)
        return df
    except Exception as e:
        return str(e)

# Streamlit UI
st.title("Amazon Database Query Assistant")
st.header("Ask questions about the Amazon database")

nl_query = st.text_input("Enter your question:")

if st.button("Generate SQL & Execute"):
    if nl_query.strip():
        sql_query = generate_sql_query(nl_query)
        st.write("### Generated SQL Query:")
        st.code(sql_query, language='sql')
        
        results = execute_query(sql_query)
        st.write("### Query Results:")
        if isinstance(results, pd.DataFrame) and not results.empty:
            st.dataframe(results)
        else:
            st.write("No results found or an error occurred.")
