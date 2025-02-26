name: CI/CD Pipeline

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
permissions:
  contents: write  # ✅ GITHUB_TOKEN에 쓰기 권한 추가 (기본적으로 read-only)
  
jobs:
  # DevSecX_workflow 프로젝트 실행 및 결과 반영
  scan-and-llm:
    runs-on: ubuntu-latest
    steps:
      # 1️⃣ 호출한 리포지토리 체크아웃
      - name: Checkout Caller Repository
        uses: actions/checkout@v3
        with:
          persist-credentials: true  # Fork된 저장소에서도 인증 유지

      # 2️⃣ DevSecX Workflow 실행
      - name: Run DevSecX Workflow
        uses: avox-dev/DevSecX_workflow@main
        env:
          MY_API_KEY: ${{ secrets.MY_API_KEY }}

      # 3️⃣ 아티팩트 다운로드 (LLM 분석 결과)
      - name: Download LLM Response
        uses: actions/download-artifact@v4
        with:
          name: llm-response
          path: ./

      # 4️⃣ 아티팩트 다운로드 (보안 수정된 소스 코드)
      - name: Download Fixed Source Code
        uses: actions/download-artifact@v4
        with:
          name: llm-newcode
          path: ./new

      # 5️⃣ 변경 사항 커밋 & 푸시 (호출한 리포지토리에)
      - name: Commit and Push Changes to Caller Repo
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"

          git add response.json
          git add new/ || echo "No new folder to add"

          git commit -m "🔄 Auto-commit: LLM scan results & fixed code" || echo "No changes to commit"
          git push origin main || echo "No changes to push"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
