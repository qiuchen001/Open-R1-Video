export WANDB_PROJECT=Qwen2-VL-7B-Video-GRPO
export WANDB_NAME=llava-video-4k-remove-formatreward-matchletterreward-f16

mkdir -p /mnt/data/ai-ground/projects/Open-R1-Video/ckpt/$WANDB_PROJECT/$WANDB_NAME
VIDEO_MAX_PIXELS=50176 \
FPS_MAX_FRAMES=12 \
MAX_PIXELS=1003520 \
CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun --nproc_per_node="4" \
    --nnodes="1" \
    --node_rank="0" \
    --master_addr="127.0.0.1" \
    --master_port="12352" \
    src/open_r1_video/grpo.py \
    --deepspeed scripts/zero3_offload.json \
    --output_dir /mnt/data/ai-ground/projects/Open-R1-Video/ckpt/$WANDB_PROJECT/$WANDB_NAME \
    --model_name_or_path /mnt/data/ai-ground/models/Qwen/Qwen2-VL-7B-Instruct \
    --dataset_name LLaVA-Video-large-swift \
    --jsonl_path /mnt/data/ai-ground/dataset/Xiaodong/open-r1-video-4k/LLaVA-Video-large-swift-origin.jsonl \
    --max_prompt_length 8192 \
    --learning_rate 1e-6 \
    --beta 0.1 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --num_generations 2 \
    --logging_steps 1 \
    --bf16 true \
    --torch_dtype bfloat16 \
    --data_seed 42 \
    --gradient_checkpointing true \
    --attn_implementation flash_attention_2 \
    --num_train_epochs 1 \
    --run_name $WANDB_NAME \
    --save_steps 10 \
    --save_only_model true \
    --report_to swanlab