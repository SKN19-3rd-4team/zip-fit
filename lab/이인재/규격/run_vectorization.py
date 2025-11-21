# 벡터화 실행 스크립트
import asyncio
import sys
from vectorizer import Vectorizer


async def main():
    """벡터화 실행"""
    batch_size = 10
    
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            print("사용법: python run_vectorization.py [배치크기]")
            sys.exit(1)
    
    print(f"벡터화 시작 (배치 크기: {batch_size})")
    print("="*80)
    
    vectorizer = Vectorizer()
    
    try:
        progress = await vectorizer.vectorize_all(batch_size)
        
        print("\n" + "="*80)
        print("벡터화 진행 상황:")
        print("="*80)
        for category, stats in progress.items():
            print(f"{category}: {stats['vectorized']}/{stats['total']} "
                  f"({stats['percentage']:.2f}%)")
        
        print("\n벡터화 완료")
    
    except KeyboardInterrupt:
        print("\n사용자가 중단했습니다")
    except Exception as e:
        print(f"\n오류 발생: {e}")
    finally:
        vectorizer.close()


if __name__ == "__main__":
    asyncio.run(main())
