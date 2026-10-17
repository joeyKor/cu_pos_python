"""
금전문함(돈통/금고) 자동 오픈 및 제어 매니저
- USB/시리얼(COM 포트) 트리거 지원 (PL2303, CH340, FTDI, BT-100U 등)
- 영수증 프린터(ESC/POS kick) 지원
- 비동기 백그라운드 스레드 안전 실행
- gumgo 설정 호환 및 자동 포트 감지
"""

import os
import time
import json
import threading

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

try:
    import win32print
    HAS_WIN32PRINT = True
except ImportError:
    HAS_WIN32PRINT = False

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class CashDrawerManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CashDrawerManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "json", "drawer_config.json")
        self.gumgo_config_path = os.path.join(os.path.dirname(self.base_dir), "gumgo", "config.json")
        self.config = {}
        self.config = self.load_config()

    def load_config(self):
        default_config = {
            "mode": "serial",  # "serial" or "printer"
            "port": "COM6",
            "baudrate": 9600,
            "printer_name": "Brother DCP-T720DW Printer",
            "sound_enabled": True,
            "auto_open": True,
            "open_count": 0
        }
        
        # 1. du_mart/json/drawer_config.json 우선 로드
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_config.update(data)
                return default_config
            except Exception as e:
                print(f"[CashDrawerManager] drawer_config.json 로드 실패: {e}")

        # 2. gumgo/config.json 에서 가져오기
        if os.path.exists(self.gumgo_config_path):
            try:
                with open(self.gumgo_config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_config.update(data)
            except Exception as e:
                print(f"[CashDrawerManager] gumgo config.json 로드 실패: {e}")

        # 3. 자동 감지 시도 (포트가 비어있거나 없는 경우)
        detected_port = self.auto_detect_port()
        if detected_port:
            default_config["port"] = detected_port

        self.save_config(default_config)
        return default_config

    def save_config(self, config_dict=None):
        if config_dict:
            self.config.update(config_dict)
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CashDrawerManager] 설정 저장 오류: {e}")

    def auto_detect_port(self):
        if not HAS_SERIAL:
            return ""
        try:
            ports = list(serial.tools.list_ports.comports())
            # 1. 금전함 관련 칩셋/장치 우선 탐색
            for p in ports:
                desc = (p.description or "").lower()
                if any(kw in desc for kw in ["prolific", "ch340", "ftdi", "usb serial", "usb-to-serial", "pl2303"]):
                    return p.device
            # 2. 첫 번째 사용 가능한 COM 포트
            if ports:
                return ports[0].device
        except Exception as e:
            print(f"[CashDrawerManager] 포트 자동 감지 오류: {e}")
        return "COM6"

    def get_available_ports(self):
        if not HAS_SERIAL:
            return []
        try:
            ports = serial.tools.list_ports.comports()
            return [f"{p.device} ({p.description})" for p in ports]
        except Exception as e:
            print(f"[CashDrawerManager] 포트 목록 조회 오류: {e}")
            return []

    def get_available_printers(self):
        if not HAS_WIN32PRINT:
            return []
        try:
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            return printers
        except Exception as e:
            print(f"[CashDrawerManager] 프린터 목록 조회 오류: {e}")
            return []

    def play_sound(self):
        if self.config.get("sound_enabled", True) and HAS_WINSOUND:
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

    def open_drawer(self):
        """동기식으로 금전문함 열기 실행"""
        mode = self.config.get("mode", "serial")
        success = False
        message = ""

        try:
            if mode == "serial":
                success, message = self._open_via_serial()
            else:
                success, message = self._open_via_printer()
        except Exception as e:
            success = False
            message = str(e)

        if success:
            count = self.config.get("open_count", 0) + 1
            self.config["open_count"] = count
            self.save_config()
            self.play_sound()
            print(f"[CashDrawerManager] [OK] 금고 오픈 완료: {message} (누적: {count}회)")
        else:
            print(f"[CashDrawerManager] [FAIL] 금고 오픈 실패: {message}")

        return success, message

    def _open_via_serial(self):
        if not HAS_SERIAL:
            return False, "pyserial 라이브러리가 설치되어 있지 않습니다."

        port = self.config.get("port", "COM6")
        if not port:
            port = self.auto_detect_port()
        if not port:
            return False, "연결된 COM 포트가 없습니다."

        baudrate = self.config.get("baudrate", 9600)

        # 다양한 USB 금전함 트리거 호환 신호 (ESC/POS pin2, pin5, ASCII 문자)
        esc_pos_cmd1 = b"\x1b\x70\x00\x19\xfa"
        esc_pos_cmd2 = b"\x1b\x70\x01\x19\xfa"
        trigger_chars = b"\x071p\r\n"

        ser = None
        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                write_timeout=1
            )

            # DTR / RTS 펄스 (하드웨어 트리거용)
            ser.dtr = True
            ser.rts = True
            time.sleep(0.05)

            # ESC/POS 및 트리거 바이트 전송
            ser.write(esc_pos_cmd1)
            ser.flush()
            ser.write(esc_pos_cmd2)
            ser.flush()
            ser.write(trigger_chars)
            ser.flush()

            time.sleep(0.15)
            ser.dtr = False
            ser.rts = False
            time.sleep(0.05)

            return True, f"{port} 금전함 오픈 신호 전송 성공"
        except serial.SerialException as e:
            return False, f"시리얼 통신 오류 ({port}): {e}"
        except Exception as e:
            return False, f"오픈 오류: {e}"
        finally:
            if ser and ser.is_open:
                try:
                    ser.close()
                except Exception:
                    pass

    def _open_via_printer(self):
        if not HAS_WIN32PRINT:
            return False, "win32print 라이브러리가 설치되어 있지 않습니다."

        printer_name = self.config.get("printer_name", "")
        if not printer_name:
            printers = self.get_available_printers()
            if printers:
                printer_name = printers[0]
            else:
                return False, "설치된 프린터가 없습니다."

        kick_data = b"\x1b\x70\x00\x19\xfa\x1b\x70\x01\x19\xfa"

        try:
            hprinter = win32print.OpenPrinter(printer_name)
            try:
                hjob = win32print.StartDocPrinter(hprinter, 1, ("Cash Drawer Kick", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, kick_data)
                    win32print.EndPagePrinter(hprinter)
                finally:
                    win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)

            return True, f"프린터 '{printer_name}' 로 금전문함 오픈 신호 전송 성공"
        except Exception as e:
            return False, f"프린터 출력 오류: {e}"

    @classmethod
    def open_drawer_async(cls, callback=None, force=False):
        """백그라운드 데몬 스레드로 UI 지연 없이 금전문함 열기 실행"""
        def _worker():
            instance = cls()
            if not force and not instance.config.get("auto_open", True):
                return
            success, msg = instance.open_drawer()
            if not success:
                # 하드웨어 미연결 또는 가상 환경에서도 열림 피드백을 위해 사운드 출력
                instance.play_sound()
            if callback:
                try:
                    callback(success, msg)
                except Exception as e:
                    print(f"[CashDrawerManager] 콜백 실행 오류: {e}")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread


# 싱글톤 인스턴스 전역 제공
cash_drawer = CashDrawerManager()
