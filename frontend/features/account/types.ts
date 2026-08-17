export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}


export interface ChangePasswordResponse {
  message: string;
}